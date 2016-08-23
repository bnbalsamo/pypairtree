from pathlib import Path
import argparse


second_pass_e = {'/': '=',
                 ':': '+',
                 '.': ','}

second_pass_d = {'=': '/',
                 '+': ':',
                 ',': '.'}


def path_to_identifier(path, root=None, os_root_str="/"):
    if root is not None:
        path = Path(path.relative_to(root))
    if not isinstance(path, Path):
        path = path(str(path))
    x = path.parts
    if x[0] == os_root_str:
        x = x[1:]
    identifier = "".join(x)
    return desanitize_string(identifier)


def identifier_to_path(identifier, root=None):
    if root:
        x = Path(root)
    else:
        x = Path("placeholder")
    identifier = sanitize_string(identifier)
    i = [y for y in identifier]
    peices = []
    while i:
        s = i.pop(0)
        if len(i) > 0:
            s = s + i.pop(0)
        peices.append(s)
    while peices:
        x = Path(str(x), peices.pop(0))
    if root is None:
        return x.relative_to("placeholder")
    return x


def sanitize_string(i):
    new_id = []
    for c in i:
        if int(hex(ord(c)), 16) < 33 or \
                int(hex(ord(c)), 16) > 126:
            new_id.append("^{}".format(hex(ord(c))[2:]))
        elif int(hex(ord(c)), 16) in [34, 42, 43, 44, 60,
                                      61, 63, 63, 92, 94, 124]:
            new_id.append("^{}".format(hex(ord(c))[2:]))
        else:
            new_id.append(c)

    i = "".join([second_pass_e.get(x, x) for x in new_id])
    return i


def desanitize_string(i):
    i = "".join([second_pass_d.get(x, x) for x in i])
    i = [x for x in i]
    new_id = []
    while True:
        c = i.pop(0)
        if c == "^":
            first = i.pop(0)
            second = i.pop(0)
            hex_str = first + second
            new_id.append(chr(int(hex_str, 16)))
        else:
            new_id.append(c)
        if len(i) == 0:
            break
    return "".join(new_id)


def path_to_id_app():
    parser = argparse.ArgumentParser("Convert a ppath to an identifier.")

    parser.add_argument(
        "input_path",
        action="store",
        type=str
    )
    parser.add_argument(
        "--root",
        help="The root of the identifier path, if applicable",
        action="store",
        default=None,
        type=str
    )
    parser.add_argument(
        "--encapsulation",
        help="An encapsulation directory name to remove from the end of the " +
        "path, if appropriate.",
        action='store',
        default=None,
        type=str
    )
    parser.add_argument(
        "--intraobjectaddress",
        help="An intraobject address to remove from the end of the path, " +
        "if appropriate.",
        action='store',
        default=None,
        type=str
    )

    args = parser.parse_args()

    p = Path(args.input_path)
    if args.intraobjectaddress:
        p = Path(str(p).rstrip(args.intraobjectaddress))
    if args.encapsulation:
        p = Path(str(p).rstrip(args.encapsulation))
    print(path_to_identifier(p, root=args.root))


def id_to_path_app():
    parser = argparse.ArgumentParser("Convert an identifier to a ppath.")

    parser.add_argument(
        "input_identifier",
        action="store",
        type=str
    )
    parser.add_argument(
        "--root",
        help="The root to prepend to the path, if applicable",
        action="store",
        default=None,
        type=str
    )
    parser.add_argument(
        "--encapsulation",
        help="An encapsulation directory name to append to the path, " +
        "if applicable",
        action="store",
        default=None,
        type=str
    )
    parser.add_argument(
        "--intraobjectaddress",
        help="An intraobject address to append to the path, if applicable. " +
        "NOTE: Requires an encapsulation directory name also be present.",
        action='store',
        default=None,
        type=str
    )

    args = parser.parse_args()

    if args.intraobjectaddress and not args.encapsulation:
        raise ValueError("In order to construct a path with an " +
                         "intraobject address you must also supply " +
                         "an encapsulation directory name.")


    p = identifier_to_path(args.input_identifier, root=args.root)
    if args.encapsulation:
        p = Path(p, args.encapsulation)
    if args.intraobjectaddress:
        p = Path(p, args.intraobjectaddress)
    print(str(p))

