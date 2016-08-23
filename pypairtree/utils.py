from pathlib import Path


second_pass_e = {'/': '=',
                 ':': '+',
                 '.': ','}

second_pass_d = {'=': '/',
                 '+': ':',
                 ',': '.'}


def path_to_identifier(path, root=None):
    if root is not None:
        path = Path(path.relative_to(root))
    if not isinstance(path, Path):
        path = path(str(path))
    x = path.parts
    if x[0] == "/":
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
