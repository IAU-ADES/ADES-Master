import io
import builtins
import tempfile
import sys
import os
import argparse

"""convertutility.py

The set of utilities in this module allows for generalized construction 
of argument parsing utilities (argparse.ArgumentParser objects)
as well as stdin/stdout wrapping for the ADES Python conversion utilities.
The purpose of these tools is to generalize how the ADES Python conversion utilities 
define and handle I/O and text encoding when used via the command line.
"""

def call_with_files(call, args):
    """Given a callable function and a namespace of its argument, calls the provided function with temporary files/filenames as arguments if stdin/stdout are provided for input/output.

    Args:
        call (callable): A function to call with signature call(input, output) where input and output are filenames.
        args (argparse.Namespace): A set of command line arguments parsed with argparse. Required to contain "input" and "input_encoding". Optionally contains "output" and "output_encoding".
    
    Raises:
        ValueError: if the input/output are not stdin/stdout and also not interpretable as a filename
        AttributeError: if input/input_encoding or output/output_encoding are not available in args when required
    """
    def verify_filename(filename):
        """Verify that a filename is interpretable as a filename

        Args:
            filename (Any): checks that the filename is None or one of str, bytes, or os.PathLike

        Raises:
            ValueError: if the filename is not None or one of str, bytes, or os.PathLike
        """
        if filename is not None and type(filename) not in [str, bytes, os.PathLike]:
            raise ValueError(f"{filename} is not a filename")

    # open temporary files
    with tempfile.NamedTemporaryFile() as tmp_i, tempfile.NamedTemporaryFile() as tmp_o:
        args_input = getattr(args, "input")
        args_input_encoding = getattr(args, "input_encoding")
        # check if command line input is stdin
        if args_input == sys.stdin:
            # encode the stdin byte stream using the specified input encoding
            i = io.TextIOWrapper(sys.stdin.buffer, encoding=args_input_encoding)
            # write stdin to a temporary file
            with builtins.open(tmp_i.name, "w", encoding=args_input_encoding) as f:
                f.write(i.read())
            # replace function input with the name of the temporary file
            i = tmp_i.name
        else:
            # verify that the input is interpretable as a filename
            verify_filename(args_input)
            # use function input as-is
            i = args_input

        # get optional function output
        args_output = getattr(args, "output", None)

        # check if output is stdout
        if args_output == sys.stdout:
            # use temporary file name as function output
            o = tmp_o.name
        else:
            # verify that the output is interpretable as a filename
            verify_filename(args_output)
            # use function output as-is
            o = args_output

        # call the function using the newly defined input/output
        call(i, o)

        # check if original output was stdout
        if args_output == sys.stdout:
            args_output_encoding = getattr(args, "output_encoding")
            # print the contents of the temporary output file to stdout, using the desired output encoding
            o = io.TextIOWrapper(sys.stdout.buffer, encoding=args_output_encoding)
            with builtins.open(tmp_o.name, "r", encoding=args_output_encoding) as f:
                o.write(f.read())

def conversion_parser(parser=None, input_help=None, output_help=None, **kwargs):
    """Construct or modify an argparse ArgumentParser object to add an input/ouput and input/output encoding argument

    Args:
        parser (argparse.ArgumentParser, optional): A parser to add arguments to. If None, constructs a new parser. Defaults to None.
        input_help (str, optional): The help string for the input argument. Defaults to None.
        output_help (str, optional): The help string for the output argument. Defaults to None.

    Returns:
        argparse.ArgumentParser: A parser with input/ouput and input/output encoding arguments included
    """
    parser = input_parser(parser, input_help=input_help, **kwargs)
    parser = output_parser(parser, output_help=output_help, **kwargs)
    return parser

def input_parser(parser=None, input_help=None, **kwargs):
    """Construct or modify an argparse ArgumentParser object to add an input/input encoding argument

    Args:
        parser (argparse.ArgumentParser, optional): A parser to add arguments to. If None, constructs a new parser. Defaults to None.
        input_help (str, optional): The help string for the input argument. Defaults to None.

    Returns:
        argparse.ArgumentParser: A parser with input/input encoding arguments included
    """
    if parser is None:
        parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter, **kwargs)
    if input_help is None:
        input_help = "The input file to convert"
    
    parser.add_argument("input", nargs='?', type=str, default=sys.stdin, help=input_help)
    parser.add_argument("--input-encoding", default="utf-8", help="The text encoding of the input.")
    return parser

def output_parser(parser=None, output_help=None, **kwargs):
    """Construct or modify an argparse ArgumentParser object to add an output/output encoding argument

    Args:
        parser (argparse.ArgumentParser, optional): A parser to add arguments to. If None, constructs a new parser. Defaults to None.
        output_help (str, optional): The help string for the output argument. Defaults to None.

    Returns:
        argparse.ArgumentParser: A parser with output/output encoding arguments included
    """
    if parser is None:
        parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter, **kwargs)
    if output_help is None:
        output_help = "The output file to write conversion to"
    parser.add_argument("output", nargs='?', type=str, default=sys.stdout, help=output_help)
    parser.add_argument("--output-encoding", default="utf-8", help="The text encoding of the output")
    return parser
