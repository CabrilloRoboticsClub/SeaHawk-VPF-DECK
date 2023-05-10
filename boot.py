

import storage
storage.remount("/", readonly=False)
m = storage.getmount("/")
m.label = "SeaHawk-VPF-DECK"
storage.remount("/", readonly=True)