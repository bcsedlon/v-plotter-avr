#ifdef __IN_ECLIPSE__
//This is a automatic generated file
//Please do not modify this file
//If you touch this file your change will be overwritten during the next build
//This file has been generated on 2018-02-12 07:50:52

#include "Arduino.h"
#include "v.h"
#include <SPI.h>
#include <SD.h>
#include "libraries/Timer3/TimerThree.h"
#include "libraries/RTClib/RTClib.h"
#include "libraries/NewliquidCrystal/LiquidCrystal_I2C.h"
#include "libraries/Keypad_I2C/Keypad_I2C.h"
#include "libraries/Keypad/Keypad.h"
#include "libraries/OMEEPROM/OMEEPROM.h"
#include "libraries/OMMenuMgr/OMMenuMgr.h"
void serialPrintParInt(int address) ;
void serialPrintParFloat(int address) ;
void loadEEPROM() ;
void saveDefaultEEPROM() ;
void printDirectory(File dir, int numTabs) ;
void setup() ;
bool getInstrumentControl(bool a, byte mode) ;
double analogRead(int pin, int samples);
void vpInit() ;
void vpScrollTo(unsigned long l, unsigned long r) ;
void vpGoToXY(int x, int y) ;
void loop() ;
void uiOK();
void uiResetAction() ;
void uiDraw(char* p_text, int p_row, int p_col, int len) ;
void uiInstrument(bool instrument, byte mode) ;
void uiFileList() ;
void uiPrintFilePause() ;
void uiPrintFileStop() ;
void uiPrintFileStart() ;
void uiControl() ;
void uiInfo() ;
void uiSetClock() ;
void uiVpGoToXY0() ;
void uiVpGoToXY1() ;
void uiVpGoToInit() ;
void uiScreen() ;
void uiLcdPrintAlarm(bool alarmHigh, bool alarmLow) ;
void uiLcdPrintSpaces8() ;
void uiMain() ;
void leftGo(bool dir, unsigned int puls) ;
void rightGo(bool dir, unsigned int puls) ;
void printGo(unsigned int duration) ;
void timerIsr() ;

#include "v-plotter-avr.ino"


#endif
