import io
import builtins
import tempfile
import sys
import argparse

def call_with_files(call, args):
    with tempfile.NamedTemporaryFile() as tmp_i, tempfile.NamedTemporaryFile() as tmp_o:
        args_input = getattr(args, "input")
        if args_input == sys.stdin:
            i = io.TextIOWrapper(sys.stdin.buffer, encoding=args.input_encoding)
            with builtins.open(tmp_i.name, "w", encoding=args.input_encoding) as f:
                f.write(i.read())
            i = tmp_i.name
        else:
            i = args.input

        args_output = getattr(args, "output", None)

        if args_output == sys.stdout:
            o = tmp_o.name
        else:
            o = args_output
        
        call(i, o)

        if args_output == sys.stdout:
            o = io.TextIOWrapper(sys.stdout.buffer, encoding=args.output_encoding)
            with builtins.open(tmp_o.name, "r", encoding=args.output_encoding) as f:
                o.write(f.read())

def conversion_parser(parser=None, input_help=None, output_help=None, **kwargs):
    parser = input_parser(parser, input_help=input_help, **kwargs)
    parser = output_parser(parser, output_help=output_help, **kwargs)
    return parser

def input_parser(parser=None, input_help=None, **kwargs):
    if parser is None:
        parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter, **kwargs)
    if input_help is None:
        input_help = "The input file to convert"
    
    parser.add_argument("input", nargs='?', type=str, default=sys.stdin, help=input_help)
    parser.add_argument("--input-encoding", default="utf-8", help="The text encoding of the input.")
    return parser

def output_parser(parser=None, output_help=None, **kwargs):
    if parser is None:
        parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter, **kwargs)
    if output_help is None:
        output_help = "The output file to write conversion to"
    parser.add_argument("output", nargs='?', type=str, default=sys.stdout, help=output_help)
    parser.add_argument("--output-encoding", default="utf-8", help="The text encoding of the output")
    return parser
