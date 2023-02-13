FROM ros:noetic

# install ros package
RUN apt-get update && apt-get install -y \
      git \
      nano \
      qt5-default \
      python3-pyqt5 \
      ros-${ROS_DISTRO}-robot-state-publisher \
      ros-${ROS_DISTRO}-usb-cam \
      ros-${ROS_DISTRO}-xacro \
      ros-${ROS_DISTRO}-urdfdom-py \
      ros-${ROS_DISTRO}-rosserial \
      ros-${ROS_DISTRO}-rosserial-server \
      ros-${ROS_DISTRO}-urdf \
      ros-${ROS_DISTRO}-teleop-twist-keyboard \
      ros-${ROS_DISTRO}-gazebo-ros-pkgs \ 
      ros-${ROS_DISTRO}-gazebo-plugins \
      ros-${ROS_DISTRO}-gazebo-ros-control && \
    rm -rf /var/lib/apt/lists/*

# Booststrap workspace.
ENV CATKIN_DIR=/catkin_ws
RUN mkdir -p $CATKIN_DIR/src \
    && cd $CATKIN_DIR/src \
    && /bin/bash -c "source /opt/ros/${ROS_DISTRO}/setup.bash && catkin_init_workspace" \
    && cd $CATKIN_DIR \
    && /bin/bash -c "source /opt/ros/${ROS_DISTRO}/setup.bash && catkin_make"

WORKDIR $CATKIN_DIR

RUN cd $CATKIN_DIR/src \
    && git clone --depth 1 --branch noetic-devel https://github.com/verlab/hero_common.git \
    && cd $CATKIN_DIR \
    && /bin/bash -c "source /opt/ros/${ROS_DISTRO}/setup.bash \
    && rosdep install --from-paths src --ignore-src -r -y \
    && catkin_make"