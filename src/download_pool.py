# -*- coding:utf-8 -*-
import time
import queue
import threading

MAX_THREAD_NUM = 10


class DownloadPool:
    def __init__(self):
        self.queue = queue.Queue()
        self.create_download_thread()

    def create_download_thread(self):
        for i in range(MAX_THREAD_NUM):
            worker = threading.Thread(name="Thread-{}".format(i),
                                      target=self.run_task, args=(self.queue,), daemon=True)
            worker.start()

    @staticmethod
    def run_task(q):
        # 队列的元祖，0：function  1以后：为参数
        while True:
            task_info = q.get()
            fun = task_info[0]
            args = task_info[1:]
            fun(*args)
            time.sleep(5)
            q.task_done()

    def join(self):
        self.queue.join()

    def start(self, wait_jobs):
        list(map(lambda x: self.queue.put(x), wait_jobs))
