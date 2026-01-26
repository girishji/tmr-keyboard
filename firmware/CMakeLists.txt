# > west build -b tmr_kbd_nrf52840
# > west flash

# 1. Minimum version of CMake required for Zephyr
cmake_minimum_required(VERSION 3.20.0)

# 2. Tell Zephyr where to find your custom board folder
# This allows the 'boards' directory in your project to be discovered
list(APPEND BOARD_ROOT ${CMAKE_CURRENT_SOURCE_DIR})

# 3. Find the Zephyr package (this loads the build system)
find_package(Zephyr REQUIRED HINTS $ENV{ZEPHYR_BASE})

# 4. Define your project
project(tmr_keyboard)

# 5. Add your source files
# Add main.c and any other .c files you've created (like mux_logic.c)
target_sources(app PRIVATE
    src/main.c
)
