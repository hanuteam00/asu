import json
import re

def parse_args(arguments):
    _ = json.loads(arguments, strict=False)

def repair_args(args, default_arg=None):

    # Plain Text -> Wrap in default arg
    if args[0] != '{' and default_arg is not None:

        args = re.sub(r'"', r'\\"', args) # If it was plain text it probably didn't escape "
        args = '{"' + default_arg + '":"' + args + '"}'

    # Replace triple " before argument
    args = re.sub(r'"""', r'"', args)

    # Escape all \ which aren't already part of \n
    args = re.sub(r'[\\](?![\"n])', r'\\\\', args)

       

    return args



            
