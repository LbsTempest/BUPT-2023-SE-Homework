"""
Title: Queue Management for Central Air Conditioning System
Module Description:
    This module is responsible for managing the various queues in a central air conditioning system.
    It handles the organization and prioritization of rooms based on their air conditioning needs and statuses.
    The module plays a crucial role in the efficient distribution of air conditioning resources,
    ensuring that rooms are served based on predefined criteria and system state.

Main Algorithms:
    - Queue Management: Manages different queues such as ready, suspend, running, and off queues for room management.
    - Room Prioritization: Prioritizes rooms in the queues based on their current status and needs.
    - Integration with Room Module: Works in conjunction with the Room module to dynamically update and manage room statuses.

Interface Description:
    - __init__(): Initializes the queues including ready, suspend, running, and off queues.
    - add_into_off_queue(room_id): Adds a room to the off queue.
    - get_all_rooms_from_off_queue(): Retrieves all rooms from the off queue.
    - pop_off_queue(): Removes and returns the first room from the off queue.

Development Record:
    Creator: Lisheng Gong
    Creation Date: 2023/12/01
    Modifier: Lisheng Gong
    Modification Date: 2023/12/17
    Modification Content:
        - add preamble notes
    Version: 3.0.0
"""


import heapq
from datetime import datetime

from room import Room
from utils import current_temp


class Queues:
    def __init__(self) -> None:
        self.ready_queue = []
        self.suspend_queue = {}
        self.running_queue = {}
        self.off_queue = []

    def add_into_off_queue(self, room_id):
        self.off_queue.append(room_id)

    def get_all_rooms_from_off_queue(self):
        if not self.off_queue:
            return False
        return self.off_queue

    def pop_off_queue(self, room_id):
        if room_id not in self.off_queue:
            return None
        self.off_queue.remove(room_id)

    # 将服务对象加入等待/待调度队列
    def add_into_ready_queue(self, room_id, priority):
        heapq.heappush(self.ready_queue, (priority, datetime.now(), room_id))
        print(room_id, 'in ready')
        # print(self.ready_queue)
        return True

    # 从等待/待调度队列中取得优先级最高的服务对象
    def get_from_ready_queue(self):
        service_objects = heapq.nsmallest(1, self.ready_queue)
        if not service_objects:
            return None, None
        # print(service_objects)
        return service_objects[0][-1], service_objects[0][-2]  # room_id, start_waiting_time

    def get_all_rooms_from_ready_queue(self):
        if not self.ready_queue:
            return False
        return [item[2] for item in self.ready_queue]
    
    # 关机时，对象在等待队列中
    def remove_from_ready_queue(self, room_id):
        # 查找与room_id匹配的元素
        for i, (_, _, ready_room_id) in enumerate(self.ready_queue):
            if ready_room_id == room_id:
                # 移除匹配的元素
                self.ready_queue.pop(i)
                # 重新构建堆
                heapq.heapify(self.ready_queue)
                return True
        return False  # 如果没有找到匹配的元素

    # 把等待/待调度队列中优先级最高的服务对象弹出
    def pop_ready_queue(self):
        room_id = heapq.heappop(self.ready_queue)[-1]
        return room_id

    # deep_copy
    def add_into_suspend_queue(self, room: Room):
        time_now = datetime.now()
        self.suspend_queue[room] = time_now

    def get_all_rooms_from_suspend_queue(self):
        if not self.suspend_queue:
            return False
        return [key.room_id for key in self.suspend_queue.keys()]

    def pop_suspend_queue(self):
        ready_to_pop = []
        time_now = datetime.now()
        for room, start_time in self.suspend_queue.items():
            duration = (time_now - start_time).total_seconds()
            if duration >= 10 and room.current_temp >= room.target_temp:
                ready_to_pop.append(room)
        if len(ready_to_pop) == 0:
            return None
        else:
            for room in ready_to_pop:
                self.suspend_queue.pop(room)
            return ready_to_pop

    # 关机时，对象在挂起队列中
    def remove_from_suspend_queue(self, room_id):
        for room in self.suspend_queue.keys():
            if room.room_id == room_id:
                self.suspend_queue.pop(room)
                return True
        return False

    # 把服务对象加入到服务队列中
    def add_into_running_queue(self, room_id):
        self.running_queue[room_id] = room_id
        print(room_id, 'in running')
        return True

    # 把房间id为room_id的服务对象从服务队列中弹出
    def pop_service_by_room_id(self, room_id):
        self.running_queue.pop(room_id)

    # 得到服务队列中优先级最低且运行时间最长的一个服务对象
    def get_running_room_with_lowest_priority(self, room_threads):
        priority = {'HIGH': 1, 'MID': 2, 'LOW': 3}
        room_with_lowest_priority_and_longest_time = None
        lowest_priority = None
        longest_running_time = 0
        time_now = datetime.now()

        for room_id, room in room_threads.items():
            if room_id in self.running_queue.keys():
                room_priority = priority[room.current_speed]
                running_time = (time_now - room.start_time).total_seconds()

                if (lowest_priority is None or
                        room_priority > lowest_priority or
                        (room_priority == lowest_priority and running_time > longest_running_time)):

                    room_with_lowest_priority_and_longest_time = room_id
                    lowest_priority = room_priority
                    longest_running_time = running_time
        return room_with_lowest_priority_and_longest_time
