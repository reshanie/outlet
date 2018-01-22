# Copyright (c) 2018 James Patrick Dill
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import asyncio
from functools import wraps


def run_every(s, cancel_old_task=False):
    """
    This decorator will run a function every `s` seconds after the on_ready event.

    :param int s: seconds to wait
    :param bool cancel_old_task: (keyword) If True, the previous task will be canceled if still running.
    """

    def real_decorator(func):

        @wraps(func)
        async def new_func(self, loop):
            task = loop.create_task(func(self))  # create task

            while True:
                await asyncio.sleep(s)

                if cancel_old_task and not task.done():
                    task.cancel()  # if necessary, cancel still running task

                task = loop.create_task(func(self))  # create task again

        new_func.is_bg_task = True

        return new_func

    return real_decorator
