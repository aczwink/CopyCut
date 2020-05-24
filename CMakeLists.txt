cmake_minimum_required(VERSION 3.6)
project(CopyCut)
find_package(XP-CMake REQUIRED) #we need advanced cmake modules

set(CMAKE_CXX_STANDARD 17)

XPC_AutoBuildType()
XPC_OptForHost()
XPC_SetCompileDefinitions()

find_package(StdPlusPlus REQUIRED)

add_executable(CopyCut src/main.cpp src/StreamCopyCutter.hpp src/StreamCopyCutter.cpp src/MainWindow.hpp src/MainWindow.cpp)
target_link_libraries(CopyCut Std++ Std++Static)