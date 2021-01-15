import datetime
import fnmatch
import glob
import os
import pathlib
import shutil
import time
import uuid

from spine_engine.project_item.executable_item_base import ExecutableItemBase
from spine_engine.config import TOOL_OUTPUT_DIR
from spine_engine.utils.helpers import shorten
from .item_info import ItemInfo
from .utils import find_file, flatten_file_path_duplicates, is_pattern
from .output_resources import scan_for_resources


class ExecutableItem(ExecutableItemBase):
    def __init__(self, name, work_dir, output_dir, notebook_specification, logger):
        # TODO add kernel (python/julia)
        # TODO append input and nb file names to work or source dir path
        """
        Args:
            name (str): item's name
            work_dir (str): an absolute path to Spine Toolbox work directory
                or None if the Notebook should not execute in work directory
            output_dir (str): path to the directory where output files should be archived
            notebook_specification (NotebookExecutorSpecification): a notebook specification
            logger (LoggerInterface): a logger
        """
        super().__init__(name, logger)
        self._name = name
        self._work_dir = work_dir
        self._output_dir = output_dir
        self._notebook_specification = notebook_specification
        self._nb_parameters = None
        self._logger = logger
        self._valid_nb_output = None
        self._notebook_instance = None
        # FIXME passed to instance prepare method for mapping resources in spec to paths in execution_dir
        #   temporary fix for file not found errors when notebook tries to read input file and papermill.execute
        self._src_dst_mapping = {}

    @staticmethod
    def item_type():
        return ItemInfo.item_type()

    def _copy_input_files(self, paths, execution_dir):
        """
        Copies input files from given paths to work or source directory, depending on
        where the Notebook specification requires them to be.

        Args:
            paths (dict): key is path to destination file, value is path to source file
            execution_dir (str): absolute path to the execution directory

        Returns:
            bool: True if the operation was successful, False otherwise
        """
        n_copied_files = 0
        for dst, src_path in paths.items():
            if not os.path.exists(src_path):
                self._logger.msg_error.emit(f"\tFile <b>{src_path}</b> does not exist")
                print(f"\tFile <b>{src_path}</b> does not exist")
                return False
            # Join work directory path to dst (dst is the filename including possible subfolders, e.g. 'input/f.csv')
            dst_path = os.path.abspath(os.path.join(execution_dir, dst))
            # Create subdirectories if necessary
            dst_subdir, _ = os.path.split(dst)
            # print("dst: {}".format(dst))
            # print("execution_dir: {}".format(execution_dir))
            # print("dst_subdir: {}".format(dst_subdir))
            # print("src_path: {}".format(src_path))

            if not dst_subdir:
                # No subdirectories to create
                self._logger.msg.emit(f"\tCopying <b>{src_path}</b>")
                print(f"\tCopying <b>{src_path}</b>")
            else:
                # Create subdirectory structure to work or source directory
                work_subdir_path = os.path.abspath(os.path.join(execution_dir, dst_subdir))
                if not os.path.exists(work_subdir_path):
                    try:
                        os.makedirs(work_subdir_path, exist_ok=True)
                    except OSError:
                        self._logger.msg_error.emit(f"[OSError] Creating directory <b>{work_subdir_path}</b> failed.")
                        return False
                self._logger.msg.emit(f"\tCopying <b>{src_path}</b> into subdirectory <b>{os.path.sep}{dst_subdir}</b>")
            try:
                shutil.copyfile(src_path, dst_path)
                self._src_dst_mapping[dst] = dst_path
                n_copied_files += 1
            except OSError as e:
                self._logger.msg_error.emit(f"Copying file <b>{src_path}</b> to <b>{dst_path}</b> failed")
                print(f"Copying file <b>{src_path}</b> to <b>{dst_path}</b> failed")
                self._logger.msg_error.emit(f"{e}")
                if e.errno == 22:
                    msg = (
                        "The reason might be:\n"
                        "[1] The destination file already exists and it cannot be "
                        "overwritten because it is locked by Julia or some other application.\n"
                        "[2] You don't have the necessary permissions to overwrite the file.\n"
                        "To solve the problem, you can try the following:\n[1] Execute the Notebook in work "
                        "directory.\n[2] If you are executing a Julia Notebook with Julia 0.6.x, upgrade to "
                        "Julia 0.7 or newer.\n"
                        "[3] Close any other background application(s) that may have locked the file.\n"
                        "And try again.\n"
                    )
                    self._logger.msg_warning.emit(msg)
                return False
        self._logger.msg.emit(f"\tCopied <b>{n_copied_files}</b> input file(s)")
        return True

    def _copy_output_files(self, target_dir, execution_dir):
        """Copies Notebook specification output files from work directory to given target directory.

        Args:
            target_dir (str): Destination directory for Notebook specification output files
            execution_dir (str): path to the execution directory

        Returns:
            tuple: Contains two lists. The first list contains paths to successfully
            copied files. The second list contains paths (or patterns) of Notebook specification
            output files that were not found.

        Raises:
            OSError: If creating a directory fails.
        """
        failed_files = list()
        saved_files = list()
        for pattern in self._notebook_specification.output_files:
            # Create subdirectories if necessary
            dst_subdir, fname_pattern = os.path.split(pattern)
            target = os.path.abspath(os.path.join(target_dir, dst_subdir))
            if not os.path.exists(target):
                try:
                    os.makedirs(target, exist_ok=True)
                except OSError:
                    self._logger.msg_error.emit(f"[OSError] Creating directory <b>{target}</b> failed.")
                    continue
                self._logger.msg.emit(f"\tCreated result subdirectory <b>{os.path.sep}{dst_subdir}</b>")
            # Check for wildcards in pattern
            if is_pattern(pattern):
                for fname_path in glob.glob(os.path.abspath(os.path.join(execution_dir, pattern))):
                    # fname_path is a full path
                    fname = os.path.split(fname_path)[1]  # File name (no path)
                    dst = os.path.abspath(os.path.join(target, fname))
                    full_fname = os.path.join(dst_subdir, fname)
                    try:
                        shutil.copyfile(fname_path, dst)
                        saved_files.append((full_fname, dst))
                    except OSError:
                        self._logger.msg_error.emit(f"[OSError] Copying pattern {fname_path} to {dst} failed")
                        failed_files.append(full_fname)
            else:
                output_file = os.path.abspath(os.path.join(execution_dir, pattern))
                if not os.path.isfile(output_file):
                    failed_files.append(pattern)
                    continue
                dst = os.path.abspath(os.path.join(target, fname_pattern))
                try:
                    shutil.copyfile(output_file, dst)
                    saved_files.append((pattern, dst))
                except OSError:
                    self._logger.msg_error.emit(f"[OSError] Copying output file {output_file} to {dst} failed")
                    failed_files.append(pattern)
        return saved_files, failed_files

    def _copy_program_files(self, execution_dir):
        """Copies Notebook specification source files to base directory."""
        # Make work directory anchor with path as tooltip
        work_anchor = "<a style='color:#99CCFF;' title='{0}' href='file:///{0}'>work directory</a>".format(
            execution_dir
        )
        self._logger.msg.emit(
            f"*** Copying Notebook specification <b>{self._notebook_specification.name}</b> program files to {work_anchor} ***"
        )
        print(f"*** Copying Notebook specification <b>{self._notebook_specification.name}</b> program files to {work_anchor} ***")
        n_copied_files = 0
        for source_pattern in self._notebook_specification.includes:
            dir_name, file_pattern = os.path.split(source_pattern)
            src_dir = os.path.join(self._notebook_specification.path, dir_name)
            dst_dir = os.path.join(execution_dir, dir_name)
            # Create the destination directory
            try:
                os.makedirs(dst_dir, exist_ok=True)
            except OSError:
                self._logger.msg_error.emit(f"Creating directory <b>{dst_dir}</b> failed")
                print(f"Creating directory <b>{dst_dir}</b> failed")
                return False
            # Copy file if necessary
            if file_pattern:
                for src_file in glob.glob(os.path.abspath(os.path.join(src_dir, file_pattern))):
                    dst_file = os.path.abspath(os.path.join(dst_dir, os.path.basename(src_file)))
                    try:
                        shutil.copyfile(src_file, dst_file)
                        n_copied_files += 1
                        self._src_dst_mapping[source_pattern] = dst_file
                    except OSError:
                        self._logger.msg_error.emit(f"\tCopying file <b>{src_file}</b> to <b>{dst_file}</b> failed")
                        print(f"\tCopying file <b>{src_file}</b> to <b>{dst_file}</b> failed")
                        return False
        if n_copied_files == 0:
            self._logger.msg_warning.emit("Warning: No files copied")
            print("Warning: No files copied")
        else:
            self._logger.msg.emit(f"\tCopied <b>{n_copied_files}</b> file(s)")
            print(f"\tCopied <b>{n_copied_files}</b> file(s)")
        return True

    def _create_input_dirs(self, execution_dir):
        """Iterates items in required input files and check
        if there are any directories to create. Create found
        directories directly to work or source directory.

        Args:
            execution_dir (str): the execution directory

        Returns:
            bool: True if the operation was successful, False otherwiseBoolean variable depending on success
        """
        for required_path in self._notebook_specification.input_files:
            path, filename = os.path.split(required_path)
            if filename:
                continue
            path_to_create = os.path.join(execution_dir, path)
            try:
                os.makedirs(path_to_create, exist_ok=True)
            except OSError:
                self._logger.msg_error.emit(f"[OSError] Creating directory {path_to_create} failed. Check permissions.")
                return False
            self._logger.msg.emit(f"\tDirectory <b>{os.path.sep}{path}</b> created")
        return True

    def _create_output_dirs(self, execution_dir):
        """Makes sure that work directory has the necessary output directories for Notebook output files.
        Checks only "output_files" list. Alternatively you can add directories to "input_files" list
        in the notebook definition file.

        Args:
            execution_dir (str): a path to the execution directory

        Returns:
            bool: True for success, False otherwise.

        Raises:
            OSError: If creating an output directory to work fails.
        """
        for out_file_path in self._notebook_specification.output_files:
            dirname = os.path.split(out_file_path)[0]
            if not dirname:
                continue
            dst_dir = os.path.join(execution_dir, dirname)
            try:
                os.makedirs(dst_dir, exist_ok=True)
            except OSError:
                self._logger.msg_error.emit(f"Creating work output directory '{dst_dir}' failed")
                return False
        return True

    def _output_resources_forward(self):
        """See base class."""
        return scan_for_resources(self, self._notebook_specification, self._output_dir, False)

    def stop_execution(self):
        return NotImplementedError

    def execute(self, forward_resources, backward_resources):
        """
            This executes a notebook with papermill and parses the output from the resulting nbformat.NotebookNode
            the output is then passed onto the next solid in the pipeline
            :return: notebook output evaluated as python expression using eval()
        """
        # execute notebook with papermill
        if not super().execute(forward_resources, backward_resources):
            return False
        if self._notebook_specification is None:
            self._logger.msg_warning.emit(f"Notebook executor <b>{self.name}</b> has no Notebook specification to "
                                          f"execute")
            print(f"Notebook executor <b>{self.name}</b> has no Notebook specification to execute")
            return False
        # print("self._work_dir: {}".format(self._work_dir))
        execution_dir = _execution_directory(self._work_dir, self._notebook_specification)
        if execution_dir is None:
            return False
        if self._work_dir is not None:
            work_or_source = "work"
            # Make work directory anchor with path as tooltip
            work_anchor = (
                    "<a style='color:#99CCFF;' title='"
                    + execution_dir
                    + "' href='file:///"
                    + execution_dir
                    + "'>work directory</a>"
            )
            self._logger.msg.emit(
                f"*** Copying Notebook executor specification <b>{self._notebook_specification.name}"
                f"</b> source files to {work_anchor} ***"
            )
            if not self._copy_program_files(execution_dir):
                self._logger.msg_error.emit("Copying program files to work directory failed.")
                print("Copying program files to work directory failed.")
                return False
        else:
            work_or_source = "source"
        # Make source directory anchor with path as tooltip
        anchor = (
            f"<a style='color:#99CCFF;' title='{execution_dir}'"
            f"href='file:///{execution_dir}'>{work_or_source} directory</a>"
        )
        self._logger.msg.emit(
            f"*** Executing Notebook specification <b>{self._notebook_specification.name}</b> in {anchor} ***"
        )
        print(f"*** Executing Notebook specification <b>{self._notebook_specification.name}</b> in {anchor} ***")
        # Find required input files for ToolInstance (if any)
        if self._notebook_specification.input_files:
            self._logger.msg.emit("*** Checking Notebook specification requirements ***")
            print("*** Checking Notebook specification requirements ***")
            n_dirs, n_files = _count_files_and_dirs(self._notebook_specification.input_files)
            if n_files > 0:
                self._logger.msg.emit("*** Searching for required input files ***")
                print("*** Searching for required input files ***")
                # print(forward_resources)
                file_paths = flatten_file_path_duplicates(
                    self._find_input_files(forward_resources), self._logger, log_duplicates=True
                )
                # print("file paths: {}".format(file_paths))
                not_found = [k for k, v in file_paths.items() if v is None]
                if not_found:
                    self._logger.msg_error.emit(f"Required file(s) <b>{', '.join(not_found)}</b> not found")
                    print(f"Required file(s) <b>{', '.join(not_found)}</b> not found")
                    return False
                self._logger.msg.emit(f"*** Copying input files to {work_or_source} directory ***")
                print(f"*** Copying input files to {work_or_source} directory ***")
                # Copy input files to ToolInstance work or source directory
                if not self._copy_input_files(file_paths, execution_dir):
                    self._logger.msg_error.emit("Copying input files failed. Notebook execution aborted.")
                    print("Copying input files failed. Notebook execution aborted.")
                    return False
            if n_dirs > 0:
                self._logger.msg.emit(f"*** Creating input subdirectories to {work_or_source} directory ***")
                print(f"*** Creating input subdirectories to {work_or_source} directory ***")
                if not self._create_input_dirs(execution_dir):
                    # Creating directories failed -> abort
                    self._logger.msg_error.emit("Creating input subdirectories failed. Notebook specification aborted.")
                    print("Creating input subdirectories failed. Notebook specification aborted.")
                    return False
        if not self._create_output_dirs(execution_dir):
            self._logger.msg_error.emit("Creating output subdirectories failed. Notebook execution aborted.")
            print("Creating output subdirectories failed. Notebook execution aborted.")
            return False
        self._notebook_instance = self._notebook_specification.create_notebook_instance(execution_dir, self._logger, self)
        # TODO implement below for expanding labelled args for notebook params
        # Expand cmd_line_args from resources
        # labelled_args = labelled_resource_args(forward_resources + backward_resources)
        # for k, label in enumerate(self._cmd_line_args):
        #     arg = labelled_args.get(label)
        #     if arg is not None:
        #         self._cmd_line_args[k] = arg
        try:
            # print("self._src_dst_mapping: {}".format(self._src_dst_mapping))
            self._notebook_instance.prepare(self._src_dst_mapping)
        except RuntimeError as error:
            self._logger.msg_error.emit(f"Failed to prepare notebook instance: {error}")
            print(f"Failed to prepare notebook instance: {error}")
            return False
        self._logger.msg.emit(f"*** Starting instance of Notebook specification <b>{self._notebook_specification.name}</b> ***")
        print(f"*** Starting instance of Notebook specification <b>{self._notebook_specification.name}</b> ***")
        return_code = self._notebook_instance.execute()
        self._handle_output_files(return_code, execution_dir)
        self._notebook_instance = None
        return return_code == 0

    def _find_input_files(self, resources):
        """
        Iterates required input  files in Notebook specification and looks for them in the given resources.

        Args:
            resources (list): resources available

        Returns:
            Dictionary mapping required files to path where they are found, or to None if not found
        """
        file_paths = dict()
        for required_path in self._notebook_specification.input_files:
            _, filename = os.path.split(required_path)
            if not filename:
                # It's a directory
                continue
            file_paths[required_path] = find_file(filename, resources)
        return file_paths

    def _handle_output_files(self, return_code, execution_dir):
        """Copies Notebook specification output files from work directory to result directory.

        Args:
            return_code (bool): Notebook specification process return value
            execution_dir (str): path to the execution directory
        """
        output_dir_timestamp = _create_output_dir_timestamp()  # Get timestamp when Notebook finished
        # Create an output folder with timestamp and copy output directly there
        if return_code != 0:
            result_path = os.path.abspath(os.path.join(self._output_dir, "failed", output_dir_timestamp))
        else:
            result_path = os.path.abspath(os.path.join(self._output_dir, output_dir_timestamp))
        try:
            os.makedirs(result_path, exist_ok=True)
        except OSError:
            self._logger.msg_error.emit(
                "\tError creating timestamped output directory. "
                "Notebook specification output files not copied. Please check directory permissions."
            )
            return
        # Make link to output folder
        result_anchor = (
            f"<a style='color:#BB99FF;' title='{result_path}'" f"href='file:///{result_path}'>results directory</a>"
        )
        self._logger.msg.emit(f"*** Archiving output files to {result_anchor} ***")
        if self._notebook_specification.output_files:
            saved_files, failed_files = self._copy_output_files(result_path, execution_dir)
            if not saved_files:
                # If no files were saved
                self._logger.msg_error.emit("\tNo files saved")
            else:
                # If there are saved files
                # Split list into filenames and their paths
                filenames, _ = zip(*saved_files)
                self._logger.msg.emit("\tThe following output files were saved to results directory")
                for filename in filenames:
                    self._logger.msg.emit(f"\t\t<b>{filename}</b>")
            if failed_files:
                # If saving some or all files failed
                self._logger.msg_warning.emit("\tThe following output files were not found")
                for failed_file in failed_files:
                    failed_fname = os.path.split(failed_file)[1]
                    self._logger.msg_warning.emit(f"\t\t<b>{failed_fname}</b>")
        else:
            tip_anchor = (
                "<a style='color:#99CCFF;' title='When you add output files to the Notebook specification,\n "
                "they will be archived into results directory. Also, output files are passed to\n "
                "subsequent project items.' href='#'>Tip</a>"
            )
            self._logger.msg_warning.emit(f"\tNo output files defined for this Notebook specification. {tip_anchor}")

    @classmethod
    def from_dict(cls, item_dict, name, project_dir, app_settings, specifications, logger):
        """See base class."""
        execute_in_work = item_dict["execute_in_work"]
        if execute_in_work:
            work_dir = app_settings.value("appSettings/workDir")
            if not work_dir:
                logger.msg_error.emit(f"Error: Work directory not set for project item {name}")
                work_dir = None
        else:
            work_dir = None
        data_dir = pathlib.Path(project_dir, ".spinetoolbox", "items", shorten(name))
        output_dir = pathlib.Path(data_dir, TOOL_OUTPUT_DIR)
        specification_name = item_dict["specification"]
        specification = ExecutableItemBase._get_specification(
            name, ItemInfo.item_type(), specification_name, specifications, logger
        )
        return cls(name, work_dir, output_dir, specification, logger)


def _count_files_and_dirs(paths):
    """
    Counts the number of files and directories in given paths.

    Args:
        paths (list): list of paths

    Returns:
        Tuple containing the number of required files and directories.
    """
    n_dir = 0
    n_file = 0
    for path in paths:
        _, filename = os.path.split(path)
        if not filename:
            n_dir += 1
        else:
            n_file += 1
    return n_dir, n_file


def _create_output_dir_timestamp():
    """ Creates a new timestamp string that is used as Notebook output
    directory.

    Returns:
        Timestamp string or empty string if failed.
    """
    try:
        # Create timestamp
        stamp = datetime.datetime.fromtimestamp(time.time())
    except OverflowError:
        return ""
    extension = stamp.strftime("%Y-%m-%dT%H.%M.%S")
    return extension


def _execution_directory(work_dir, notebook_specification):
    """
    Returns the path to the execution directory, depending on ``execute_in_work``.

    If ``execute_in_work`` is ``True``, a new unique path will be returned.
    Otherwise, the main program file path from notebook specification is returned.

    Returns:
        str: a full path to next basedir
    """
    # print(notebook_specification.path)
    if work_dir is not None:
        basedir = os.path.join(work_dir, _unique_dir_name(notebook_specification))
        try:
            os.makedirs(basedir, exist_ok=True)
        except OSError:
            print(f"Creating execution directory '{basedir}' failed")
            return None
        return basedir
    return notebook_specification.path


def _find_files_in_pattern(pattern, available_file_paths):
    """
    Returns a list of files that match the given pattern.

    Args:
        pattern (str): file pattern
        available_file_paths (list): list of available file paths from upstream items
    Returns:
        list: List of (full) paths
    """
    extended_pattern = os.path.join("*", pattern)  # Match all absolute paths.
    return fnmatch.filter(available_file_paths, extended_pattern)


def _unique_dir_name(notebook_specification):
    """Builds a unique name for Notebook's work directory."""
    return notebook_specification.short_name + "__" + uuid.uuid4().hex + "__toolbox"
