from vircuum.tradeapi.common import isnumber
import random

class TradeAPI(object):
    TIME_PER_LOOP = 1

    def __init__(self, *args, **kwargs):
        self.prev_last = 500
        self.dummy_loop = 0
        self.dummy_loop_dir = 0

    def ticker(self):

        return (self.dummy_last(), )

    def balance(self):
        return 100.0

    def dummy_last(self):

        def rand(dir = None):
            if dir is None:
                dir = self.dummy_loop_dir

            if dir == 0:
                self.prev_last += float(random.randint(-50, 50)) * 1
            elif dir > 0:
                self.prev_last += float(random.randint(0, 100)) * 1
            elif dir < 0:
                self.prev_last += float(random.randint(-100, 0)) * 1

            return self.prev_last


        while True:
            if self.dummy_loop > 0:
                self.dummy_loop -= 1
                return rand()

            last = str(raw_input("New last?"))
            try:
                if last == "":
                    return rand(dir = 0)
                elif last.startswith("loopup"):
                    self.dummy_loop_dir = 1
                    self.dummy_loop = int(last[6:])
                    return rand()
                elif last.startswith("loopdown"):
                    self.dummy_loop_dir = -1
                    self.dummy_loop = int(last[8:])
                    return rand()
                elif last.startswith("loop"):
                    self.dummy_loop_dir = 0
                    self.dummy_loop = int(last[4:])
                    return rand()
                elif last.startswith("*"):
                    self.prev_last = self.prev_last * float(last[1:])
                elif last.startswith("*"):
                    self.prev_last = self.prev_last * float(last[1:])
                    return self.prev_last
                elif last.startswith("/"):
                    self.prev_last = self.prev_last / float(last[1:])
                    return self.prev_last
                elif last.startswith("+"):
                    self.prev_last = self.prev_last + float(last[1:])
                    return self.prev_last
                elif last.startswith("-"):
                    self.prev_last = self.prev_last - float(last[1:])
                    return self.prev_last
                elif isnumber(last):
                    self.prev_last = float(last)
                    return self.prev_last
            except:
                pass

            continue

