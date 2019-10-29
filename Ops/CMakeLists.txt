#[[===================================================================
Copyright 2019 Matthias Komm, Vilius Cepaitis, Robert Bainbridge, 
Alex Tapper, Oliver Buchmueller. All Rights Reserved. 
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0
    
Unless required by applicable law or agreed to in writing, 
software distributed under the License is distributed on an "AS IS" 
BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express 
or implied.See the License for the specific language governing 
permissions and limitations under the License.
===================================================================]]


project(ROOT-TF-pipeline)
cmake_minimum_required(VERSION 3.0)
set(CMAKE_MODULE_PATH ${PROJECT_SOURCE_DIR} ${CMAKE_MODULE_PATH})

if(NOT CMAKE_BUILD_TYPE)
    message(STATUS "No build type specific - will use 'Release' as default")
    set(CMAKE_BUILD_TYPE "Release" CACHE STRING
        "Choose the type of build, options are: Debug Release
        RelWithDebInfo MinSizeRel."
        FORCE
    )
endif(NOT CMAKE_BUILD_TYPE)

if(CMAKE_CXX_COMPILER_ID STREQUAL "GNU")
    set(CMAKE_CXX_FLAGS "\
        -Wall -Wextra -Wshadow -Wnon-virtual-dtor -pedantic \
        -Wold-style-cast -Wcast-align -Wunused -Woverloaded-virtual \
        -Wconversion -Wsign-conversion -Wmisleading-indentation \
        -Wduplicated-cond -Wlogical-op \
        -Wnull-dereference -Wuseless-cast -Wdouble-promotion \
        ${CMAKE_CXX_FLAGS}"
    )
endif(CMAKE_CXX_COMPILER_ID STREQUAL "GNU")

macro(copy_file_if_changed in_file out_file target)  
    add_custom_command (
	    TARGET     ${target}
	    POST_BUILD
	    COMMAND    ${CMAKE_COMMAND}
	    ARGS       -E copy_if_different ${in_file} ${out_file}
	    COMMENT "Copying file: ${in_file} to: ${out_file}"
    )
endmacro(copy_file_if_changed)

find_package(PythonInterp 2.7 REQUIRED)
find_package(TensorFlow 1.6 REQUIRED)
find_package(ROOT 6 REQUIRED)


set(MODULENAME "rtf" CACHE STRING "Module name")
message(STATUS "Module name: ${MODULENAME}")

set(PACKAGEDIR ${CMAKE_INSTALL_PREFIX}/${MODULENAME})
message(STATUS "Install dir: ${SITEPACKDIR}")

add_definitions(${TensorFlow_DEFINITIONS})

message(STATUS "ROOT definitions: ${ROOT_DEFINITIONS}")
message(STATUS "TensorFlow definitions: ${TensorFlow_DEFINITIONS}")

include_directories(
    SYSTEM ${TensorFlow_INCLUDE_DIRS} 
    SYSTEM ${ROOT_INCLUDE_DIR}
)

add_library(RootReader
    MODULE
    RootReader.cc
)
target_link_libraries(RootReader ${TensorFlow_LIBRARY} ${ROOT_LIBRARIES} -lTreePlayer)
install(TARGETS RootReader LIBRARY DESTINATION ${PACKAGEDIR})

add_library(ClassificationWeights
    MODULE
    ClassificationWeights.cc
)
target_link_libraries(ClassificationWeights ${TensorFlow_LIBRARY} ${ROOT_LIBRARIES})
install(TARGETS ClassificationWeights LIBRARY DESTINATION ${PACKAGEDIR})

add_library(FakeBackground
    MODULE
    FakeBackground.cc
)
target_link_libraries(FakeBackground ${TensorFlow_LIBRARY} ${ROOT_LIBRARIES})
install(TARGETS FakeBackground LIBRARY DESTINATION ${PACKAGEDIR})

add_library(Resampler
    MODULE
    Resampler.cc
)
target_link_libraries(Resampler ${TensorFlow_LIBRARY})
install(TARGETS Resampler LIBRARY DESTINATION ${PACKAGEDIR})

set(pythonfiles
    __init__.py
    root_reader.py
    resampler.py
    fake_background.py
    classification_weights.py
)

foreach(pyfile ${pythonfiles})
    copy_file_if_changed(
        ${CMAKE_SOURCE_DIR}/${pyfile}
        ${CMAKE_CURRENT_BINARY_DIR}/${pyfile}
        RootReader
    )
    install(FILES ${CMAKE_SOURCE_DIR}/${pyfile} DESTINATION ${PACKAGEDIR})
endforeach(pyfile)

enable_testing()

add_test(
    NAME test_rtf
    COMMAND ${PYTHON_EXECUTABLE} -c "import ${MODULENAME}"
    WORKING_DIRECTORY ${CMAKE_INSTALL_PREFIX}
)

