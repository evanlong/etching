#
# embedXcode
# ----------------------------------
# Embedded Computing on Xcode 4
#
# Copyright © Rei VILO, 2010-2012
# Licence CC = BY NC SA
#

# References and contribution
# ----------------------------------
# See About folder
# 

# The Maple reset script —which sends control signals over 
# the USB-serial connection to restart and enter the bootloader—
# is written in Python and requires the PySerial library. 
#
# Instructions available at http://leaflabs.com/docs/unix-toolchain.html#os-x
# Download PySerial library from http://pypi.python.org/pypi/pyserial
#

# Maple specifics
# ----------------------------------
#
PLATFORM         := MapleIDE
PLATFORM_TAG     := MAPLE_IDE
APPLICATION_PATH := /Applications/MapleIDE.app/Contents/Resources/Java

UPLOADER          = dfu-util
DFU_UTIL_PATH     = $(APPLICATION_PATH)/hardware/tools/arm/bin
DFU_UTIL          = $(DFU_UTIL_PATH)/dfu-util
DFU_UTIL_OPTS     = -a$(call PARSE_BOARD,$(BOARD_TAG),upload.altID) -d $(call PARSE_BOARD,$(BOARD_TAG),upload.usbID)
DFU_RESET         = $(UTILITIES_PATH)/reset.py

APP_TOOLS_PATH   := $(APPLICATION_PATH)/hardware/tools/arm/bin
CORE_LIB_PATH    := $(APPLICATION_PATH)/hardware/leaflabs/cores/maple
APP_LIB_PATH     := $(APPLICATION_PATH)/libraries
BOARDS_TXT       := $(APPLICATION_PATH)/hardware/leaflabs/boards.txt

# Sketchbook/Libraries path
# wildcard required for ~ management
#
ifeq ($(USER_PATH)/Library/MapleIDE/preferences.txt,)
    $(error Error: run Mpide once and define sketchbook path)
endif

ifeq ($(wildcard $(SKETCHBOOK_DIR)),)
    SKETCHBOOK_DIR = $(shell grep sketchbook.path $(USER_PATH)/Library/MapleIDE/preferences.txt | cut -d = -f 2)
endif
ifeq ($(wildcard $(SKETCHBOOK_DIR)),)
    $(error Error: sketchbook path not found)
endif
USER_LIB_PATH  = $(wildcard $(SKETCHBOOK_DIR)/Libraries)
CORE_AS_SRCS   = $(wildcard $(CORE_LIB_PATH)/*.S) # */


# Rules for making a c++ file from the main sketch (.pde)
#
PDEHEADER      = \\\#include \"WProgram.h\"  


# Tool-chain names
#
CC      = $(APP_TOOLS_PATH)/arm-none-eabi-gcc
CXX     = $(APP_TOOLS_PATH)/arm-none-eabi-g++
AR      = $(APP_TOOLS_PATH)/arm-none-eabi-ar
OBJDUMP = $(APP_TOOLS_PATH)/arm-none-eabi-objdump
OBJCOPY = $(APP_TOOLS_PATH)/arm-none-eabi-objcopy
SIZE    = $(APP_TOOLS_PATH)/arm-none-eabi-size
NM      = $(APP_TOOLS_PATH)/arm-none-eabi-nm


BOARD    = $(call PARSE_BOARD,$(BOARD_TAG),build.board)
LDSCRIPT = $(call PARSE_BOARD,$(BOARD_TAG),build.linker)
VARIANT  = $(call PARSE_BOARD,$(BOARD_TAG),build.mcu)
#VARIANT_PATH = $(APPLICATION_PATH)/hardware/leaflabs/cores/maples/$(VARIANT)


MCU            = $(call PARSE_BOARD,$(BOARD_TAG),build.family)
MCU_FLAG_NAME  = mcpu
EXTRA_LDFLAGS  = -T$(CORE_LIB_PATH)/$(LDSCRIPT) -L$(APPLICATION_PATH)/hardware/leaflabs/cores/maple
EXTRA_LDFLAGS += -mthumb -Xlinker --gc-sections --print-gc-sections --march=armv7-m -Wall
EXTRA_CPPFLAGS = -fno-rtti -fno-exceptions -mthumb -march=armv7-m -nostdlib \
    -DBOARD_$(BOARD) \
    -DMCU_$(call PARSE_BOARD,$(BOARD_TAG),build.mcu) \
    -D$(call PARSE_BOARD,$(BOARD_TAG),build.vect) \
    -D$(call PARSE_BOARD,$(BOARD_TAG),build.density) \
    -DERROR_LED_PORT=$(call PARSE_BOARD,$(BOARD_TAG),build.error_led_port) \
    -DERROR_LED_PIN=$(call PARSE_BOARD,$(BOARD_TAG),build.error_led_pin) \
    -D$(PLATFORM_TAG)
    
OBJCOPYFLAGS  = -v -Obinary 







