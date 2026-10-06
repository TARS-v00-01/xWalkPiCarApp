/******************************************************************************
 * @file        xControllerCommand.h
 * @brief       Declares Controller command identifiers and protocol signals.
 *
 * @details
 * Defines typed command identifiers used for local routing and stable signal
 * numbers shared with the xWalk-rpi5-iw Controller message contract.
 *
 * @project     xWalk Firmware
 * @module      xWalkLibrary Common
 *
 * @author      Joxy John
 * @date        2026-08-06
 * @version     1.0.0
 *
 * @copyright
 * Copyright (c) 2026 Joxy John.
 * All rights reserved.
 *
 * @note
 * Developed using MISRA C++ coding guidelines.
 ******************************************************************************/

#pragma once

/******************************************************************************
 * Includes
 ******************************************************************************/

#include "xHal_Rpi5CarTypes.h"

/******************************************************************************
 * Macro definitions
 ******************************************************************************/

/** @brief Indicates that no supported command was recognized. */
#define XWALK_CNTRL_UNKNOWN_REQ (::ctrl::uint16{0x2000U})
/** @brief Requests generated command help. */
#define XWALK_CNTRL_HELP_REQ (::ctrl::uint16{0x2001U})
/** @brief Requests one SPI transfer. */
#define XWALK_CNTRL_SPI_REQ (::ctrl::uint16{0x2002U})
/** @brief Requests the bounded MCU-reset platform preflight report. */
#define XWALK_CNTRL_DOCTOR_REQ (::ctrl::uint16{0x2003U})
/** @brief Requests the twelve-channel servo-zeroing sequence. */
#define XWALK_CNTRL_SERVO_ZEROING_REQ (::ctrl::uint16{0x2004U})
/** @brief Requests interactive computer vision. */
#define XWALK_CNTRL_COMPUTER_VISION_REQ (::ctrl::uint16{0x2005U})
/** @brief Requests video recording. */
#define XWALK_CNTRL_RECORD_VIDEO_REQ (::ctrl::uint16{0x2006U})
/** @brief Requests the background-music demonstration. */
#define XWALK_CNTRL_SOUND_BACKGROUND_MUSIC_REQ (::ctrl::uint16{0x2007U})
/** @brief Requests image-grounded text conversation. */
#define XWALK_CNTRL_TEXT_VISION_TALK_REQ (::ctrl::uint16{0x2008U})
/** @brief Requests the online language-model test. */
#define XWALK_CNTRL_ONLINE_LLM_TEST_REQ (::ctrl::uint16{0x2009U})
/** @brief Requests a movement operation. */
#define XWALK_CNTRL_MOVE_REQ (::ctrl::uint16{0x200AU})
/** @brief Requests interactive keyboard control. */
#define XWALK_CNTRL_KEYBOARD_CONTROL_REQ (::ctrl::uint16{0x200BU})
/** @brief Requests obstacle avoidance. */
#define XWALK_CNTRL_AVOID_OBSTACLES_REQ (::ctrl::uint16{0x200CU})
/** @brief Requests cliff detection. */
#define XWALK_CNTRL_CLIFF_DETECTION_REQ (::ctrl::uint16{0x200DU})
/** @brief Requests face tracking. */
#define XWALK_CNTRL_STARE_AT_YOU_REQ (::ctrl::uint16{0x200EU})
/** @brief Requests red-target pursuit. */
#define XWALK_CNTRL_BULL_FIGHT_REQ (::ctrl::uint16{0x200FU})
/** @brief Requests the treasure-hunt game. */
#define XWALK_CNTRL_TREASURE_HUNT_REQ (::ctrl::uint16{0x2010U})
/** @brief Requests interactive video-car control. */
#define XWALK_CNTRL_VIDEO_CAR_REQ (::ctrl::uint16{0x2011U})
/** @brief Requests mobile-application control. */
#define XWALK_CNTRL_APP_CONTROL_REQ (::ctrl::uint16{0x2012U})
/** @brief Requests a steering turn. */
#define XWALK_CNTRL_TURN_REQ (::ctrl::uint16{0x2013U})
/** @brief Requests camera-servo control. */
#define XWALK_CNTRL_CAMERA_REQ (::ctrl::uint16{0x2014U})
/** @brief Requests a vehicle sensor reading. */
#define XWALK_CNTRL_SENSOR_REQ (::ctrl::uint16{0x2015U})
/** @brief Requests line tracking. */
#define XWALK_CNTRL_LINE_TRACK_REQ (::ctrl::uint16{0x2016U})
/** @brief Requests a named self-drive action. */
#define XWALK_CNTRL_SELF_DRIVE_REQ (::ctrl::uint16{0x2017U})
/** @brief Requests a platform sound operation. */
#define XWALK_CNTRL_SOUND_REQ (::ctrl::uint16{0x2018U})
/** @brief Requests the local voice chatbot. */
#define XWALK_CNTRL_VOICE_CHAT_REQ (::ctrl::uint16{0x2019U})
/** @brief Requests voice-active vehicle control. */
#define XWALK_CNTRL_VOICE_ACTIVE_CAR_REQ (::ctrl::uint16{0x201AU})
/** @brief Requests GPT vehicle control. */
#define XWALK_CNTRL_GPT_CAR_REQ (::ctrl::uint16{0x201BU})
/** @brief Requests wake-word vehicle control. */
#define XWALK_CNTRL_VOICE_CONTROLLED_CAR_REQ (::ctrl::uint16{0x201CU})
/** @brief Requests the spoken movement demonstration. */
#define XWALK_CNTRL_VOICE_PROMPT_CAR_REQ (::ctrl::uint16{0x201DU})
/** @brief Requests the storytelling robot. */
#define XWALK_CNTRL_STORYTELLING_ROBOT_REQ (::ctrl::uint16{0x201EU})
/** @brief Requests vehicle calibration. */
#define XWALK_CNTRL_CALIBRATE_REQ (::ctrl::uint16{0x201FU})
/** @brief Requests foreground MJPEG camera streaming. */
#define XWALK_CNTRL_VIDEO_STREAM_REQ (::ctrl::uint16{0x2020U})
