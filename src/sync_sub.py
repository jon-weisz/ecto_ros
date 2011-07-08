#!/usr/bin/python
PKG = 'ecto_ros' # this package name
import roslib; roslib.load_manifest(PKG)
import ecto
import ecto_ros, ecto_sensor_msgs
from ecto_opencv import highgui
import sys

ImageSub = ecto_sensor_msgs.Subscriber_Image
CameraInfoSub = ecto_sensor_msgs.Subscriber_CameraInfo
def do_ecto():

    sync = ecto_ros.Synchronizer('Synchronizator', subs={'image':ImageSub(topic_name='camera/rgb/image_mono',queue_size=0),
                                                         'depth':ImageSub(topic_name='camera/depth/image',queue_size=0),
                                                         'depth_info':CameraInfoSub(topic_name='camera/depth/camera_info',queue_size=0),
                                                         'image_info':CameraInfoSub(topic_name='camera/rgb/camera_info',queue_size=0),
                                                         });

    drift_printer = ecto_ros.DriftPrinter()
    
    im2mat_rgb = ecto_ros.Image2Mat()
    im2mat_depth = ecto_ros.Image2Mat()
    s1 = ecto.Strand() #imshow is not thread safe.
    
    graph = [
                sync["image"] >> im2mat_rgb["image"],
                im2mat_rgb["image"] >> highgui.imshow("rgb show", name="rgb", waitKey=5,strand=s1)[:],
                sync[:] >> drift_printer[:],
                sync["depth"] >> im2mat_depth["image"],
                im2mat_depth["image"] >> highgui.imshow("depth show", name="depth", waitKey= -1,strand=s1)[:]
            ]
    plasm = ecto.Plasm()
    plasm.connect(graph)
    ecto.view_plasm(plasm)
    
    sched = ecto.schedulers.Threadpool(plasm)
    sched.execute(8)

if __name__ == "__main__":
    ecto_ros.init(sys.argv, "ecto_node")
    do_ecto()