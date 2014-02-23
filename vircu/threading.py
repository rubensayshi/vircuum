import sys, select


def raw_input(prompt):
    """non-block raw_input"""

    sys.stdout.write(prompt)
    sys.stdout.flush()

    select.select([sys.stdin], [], [])
    return sys.stdin.readline().rstrip('\n')

