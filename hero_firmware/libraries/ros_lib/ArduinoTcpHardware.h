/*
 * Software License Agreement (BSD License)
 *
 * Copyright (c) 2011, Willow Garage, Inc.
 * All rights reserved.
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions
 * are met:
 *
 *  * Redistributions of source code must retain the above copyright
 *    notice, this list of conditions and the following disclaimer.
 *  * Redistributions in binary form must reproduce the above
 *    copyright notice, this list of conditions and the following
 *    disclaimer in the documentation and/or other materials provided
 *    with the distribution.
 *  * Neither the name of Willow Garage, Inc. nor the names of its
 *    contributors may be used to endorse or promote prducts derived
 *    from this software without specific prior written permission.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
 * "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
 * LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
 * FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
 * COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
 * INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
 * BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
 * LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
 * CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
 * LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
 * ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
 * POSSIBILITY OF SUCH DAMAGE.
 */

#ifndef ROS_ARDUINO_TCP_HARDWARE_H_
#define ROS_ARDUINO_TCP_HARDWARE_H_


#include <Arduino.h>
#if defined(ESP8266)
  #include <ESP8266WiFi.h>
  #ifdef USE_UDP_PROTOCOL
    #include <WiFiUdp.h>
  #endif
#elif defined(ESP32)
  #include <WiFi.h> // Using Espressif's WiFi.h
#else
  #include <SPI.h>
  #include <Ethernet.h>
#endif

class ArduinoHardware {
public:
  ArduinoHardware()
  {
  }

  void setConnection(IPAddress &server, int port = 11411)
  {
    server_ = server;
    serverPort_ = port;
  }

  IPAddress getLocalIP()
  {
#if defined(ESP8266) or defined(ESP32)
    #ifdef USE_UDP_PROTOCOL
    #else
      return tcp_.localIP();
    #endif
#else
    return Ethernet.localIP();
#endif
  }

  void init()
  {
    #ifdef USE_UDP_PROTOCOL
      udp_.begin(serverPort_);
    #else
      if(tcp_.connected())
      {
        tcp_.stop();
      }
      tcp_.connect(server_, serverPort_);
    #endif
  }

  int read(){
    #ifdef USE_UDP_PROTOCOL
      if (udp_.parsePacket() > 0){
        if (udp_.available() > 0){
          return udp_.read();
        }
      } else {
        udp_.stop();
        udp_.begin(serverPort_);
      }
    #else
      if (tcp_.connected())
      {
          return tcp_.read();
      }
      else
      {
        tcp_.stop();
        tcp_.connect(server_, serverPort_);
      }
    #endif
    return -1;
  }

  void write(const uint8_t* data, int length)
  {
    #ifdef USE_UDP_PROTOCOL
      udp_.beginPacket(server_, serverPort_);
      udp_.write(data, length);
      udp_.endPacket();
    #else
      tcp_.write(data, length);
    #endif
  }

  unsigned long time()
  {
    return millis();
  }

  bool connected()
  {
    #ifdef USE_UDP_PROTOCOL
      return true;
    #else
      return tcp_.connected();
    #endif
  }

protected:
#if defined(ESP8266) or defined(ESP32)
  #ifdef USE_UDP_PROTOCOL
    WiFiUDP udp_;
  #else
    WiFiClient tcp_;
  #endif
#else
  EthernetClient tcp_;
#endif
  IPAddress server_;
  uint16_t serverPort_ = 11411;
};

#endif
