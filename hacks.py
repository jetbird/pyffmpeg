import re  # module for regular expressions
import os

# the following is the string which we are going to use to find the
# text patterns we want; through the custom regular expressions
s = """Automatic encoder selection failed for output stream #0:1. Default encoder for
format 3gp (codec amr_nb) is probably disabled. Please choose an encoder manually."""


regex = r'(format)\s([\w]+)'
regex1 = r'(codec)\s([\w]+)'


r = re.search(regex, s)
r1 = re.search(regex1, s)


print(r.group(2))
print(r1.group(2))


def which_name(name):
    # get the default PATH
    path = os.getenv('PATH', os.defpath)
    return path


print(which_name(None))
