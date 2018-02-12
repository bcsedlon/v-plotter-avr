/*
 * v-plotter-avr
 */

/*
 * SD card attached to SPI bus as follows:
 * use following pins as inputs, because SD shield does not match Arduino Mega
 * MOSI - pin 11
 * MISO - pin 12
 * CLK - pin 13
 * CS - pin 10 //SS
 */

//#define __RTC__

#include "v.h"
vPlotter vp;

#include <SPI.h>
#include <SD.h>

#include "libraries/Timer3/TimerThree.h"
//#include <TimerOne.h>

const byte KPD_ROWS = 4;
const byte KPD_COLS = 4;

#define KPD_I2CADDR 0x38
char keys[KPD_ROWS][KPD_COLS] = {
		  {'1','2','3','A'},
		  {'4','5','6','B'},
		  {'7','8','9','C'},
		  {'*','0','#','D'}
};

#define OK_DELAY 500

#define TEXT_ID "V-PLOTTER-AVR"
#define VERSION 1

#define LCD_I2CADDR 0x3F
const byte LCD_ROWS = 2;
const byte LCD_COLS = 16;

#define LED_PIN 13

#define PRINT_PIN 6//12 //5
#define R_DIR_PIN 2//10 //6
#define R_PUL_PIN 3//11 //7
#define L_DIR_PIN 4//8
#define L_PUL_PIN 5//9

#define DS3231_I2C_ADDRESS 0x68

#define PRINTMODE_ADDR	4
#define SPEED_ADDR		8
#define FILEINDEX_ADDR	12
#define LINIT_ADDR		16
#define RINIT_ADDR		20
#define DISTANCE_ADDR	24
#define SCALE_ADDR		28
#define PRINTTIME_ADDR	32
#define X0_ADDR			36
#define Y0_ADDR			40
#define LDIRINV_ADDR	44
#define RDIRINV_ADDR	48
#define PRINTINV_ADDR	52

#define MESSAGE_CMD_REQUEST  	"#?"

#define MESSAGE_CMD_PARREADINT 		"#PRI"
#define MESSAGE_CMD_PARREADFLOAT 	"#PRF"
#define MESSAGE_CMD_PARWRITEINT 	"#PWI"
#define MESSAGE_CMD_PARWRITEFLOAT 	"#PWF"
#define MESSAGE_CMD_PARRELOAD 		"#PLD"

#define UISTATE_MAIN 		0
#define UISTATE_FILELIST 	1
#define UISTATE_SETCLOCK 	2
#define UISTATE_INFO 		3
#define UISTATE_EDITTEXT 	4
#define UISTATE_CONTROL 	5
//#define UISTATE_PRINTING 	6

#define STATE_STOPPED 		0
#define STATE_RUNNING 		1
#define STATE_PAUSED 		2
#define STATE_DONE	 		3

#define KPD_UP		'A'
#define KPD_DOWN 	'B'
#define KPD_LEFT 	'#'
#define KPD_RIGHT 	'D'
#define KPD_ENTER 	'*'
#define KPD_ESC 	'0'

//#include <avr/wdt.h>

//////////////////////////////////
// variables
//////////////////////////////////

byte state = 0;

char fileNames[16][16];
int fileNamesIndex;
File file;
bool sd = false;

byte secondsCounter;

//char* text;
//char* tmp_text = "0123456789ABCDEF";

DateTime nowSetClock;
DateTime now;
unsigned long milliseconds, millisecondsPrev;
unsigned long microseconds, microsecondsPrev;
bool secToggle = false;

bool stop;

char uiKeyPressed = 0;
int uiState, uiPage;
unsigned long uiKeyTime;

unsigned long cycles, cyclesPrev = 0;

unsigned long printDuration, leftPuls, rightPuls = 0;
unsigned long leftPulsPos, rightPulsPos;

// control
byte printMode, rightDirMode, rightPulMode, leftPulMode, leftDirMode;;
bool printControl, rightPulControl, rightDirControl, leftPulControl, leftDirControl;
bool printAuto, rightPulAuto, rightDirAuto, leftPulAuto, leftDirAuto;
bool leftDirInv, rightDirInv, printInv;

// parameters
unsigned int pulSpeed, scale, fileIndex, distance, leftInitLength, printTime;
unsigned int pulSpeedPrev; //, distancePrev;

int x0, y0;
/*
unsigned int fileIndex = 2;
unsigned int distance = 3000;
unsigned int leftInitLength = 2500;
*/


// inputs

// parameters
/*
unsigned int rightDirOnHour, rightDirOnMin, rightDirOffHour, rightDirOffMin;
unsigned int leftPulOnMin, leftPulOnSec, leftPulOffMin, leftPulOffSec;
float rightDirOnTemp, rightDirOffTemp, rightDirOnTempNight, rightDirOffTempNight;

bool parseCmd(String &text, const char* cmd, byte &mode, const int address=0) {
	int pos = text.indexOf(cmd);
	if(pos > -1) {
		char ch = text.charAt(pos + strlen(cmd));
		if(ch=='A') mode = 0;
		else if(ch=='0') mode = 1;
		else if(ch=='1') mode = 2;
		if(address)
			OMEEPROM::write(address, mode);
		return true;
	}
	return false;
}
*/

//#include <Wire.h>
//#include <SoftwareSerial.h>

// RTC
#ifdef __RTC__
	#include "libraries/RTClib/RTClib.h"
	RTC_DS3231 rtc;
#endif

// LCD i2c
#include "libraries/NewliquidCrystal/LiquidCrystal_I2C.h"
LiquidCrystal_I2C lcd(LCD_I2CADDR, 2, 1, 0, 4, 5, 6, 7, 3, POSITIVE);

// Keypad 4x4 i2c
#include "libraries/Keypad_I2C/Keypad_I2C.h"
#include "libraries/Keypad/Keypad.h"

class Keypad_I2C2 : public Keypad_I2C {
	unsigned long kTime;

public:
    Keypad_I2C2(char *userKeymap, byte *row, byte *col, byte numRows, byte numCols, byte address, byte width = 1) : Keypad_I2C(userKeymap, row, col, numRows, numCols, address, width) {
    };

    char Keypad_I2C2::getRawKey() {
    	/*
    	getKeys();

      	if(bitMap[3] == 1) return '*';
        if(bitMap[3] == 2) return '0';
        if(bitMap[3] == 4) return '#';
        if(bitMap[3] == 8) return 'D';

        if(bitMap[2] == 1) return '7';
        if(bitMap[2] == 2) return '8';
        if(bitMap[2] == 4) return '9';
        if(bitMap[2] == 8) return 'C';

        if(bitMap[1] == 1) return '4';
        if(bitMap[1] == 2) return '5';
        if(bitMap[1] == 4) return '6';
        if(bitMap[1] == 8) return 'B';

        if(bitMap[0] == 1) return '1';
        if(bitMap[0] == 2) return '2';
        if(bitMap[0] == 4) return '3';
        if(bitMap[0] == 8) return 'A';

        return NO_KEY;
        */

    	getKeys();

    	if(bitMap[3] == 1) return '*';
    	if(bitMap[3] == 2) return '7';
    	if(bitMap[3] == 4) return '4';
    	if(bitMap[3] == 8) return '1';

    	if(bitMap[2] == 1) return '0';
    	if(bitMap[2] == 2) return '8';
    	if(bitMap[2] == 4) return '5';
    	if(bitMap[2] == 8) return '2';

    	if(bitMap[1] == 1) return '#';
    	if(bitMap[1] == 2) return '9';
    	if(bitMap[1] == 4) return '6';
    	if(bitMap[1] == 8) return '3';

    	if(bitMap[0] == 1) return 'D';
    	if(bitMap[0] == 2) return 'C';
    	if(bitMap[0] == 4) return 'B';
    	if(bitMap[0] == 8) return 'A';

    	return NO_KEY;
    };

    char Keypad_I2C2::getKey2() {


    	getKeys();

    	if(bitMap[0] & 1) {
    	    		if(bitMap[1] & 1) {
    	    			//lcd.begin(LCD_COLS, LCD_ROWS);
    	    			/*
    	    			if(state)
    	    				state = STATE_PAUSED;
    	    			leftPuls = 0;
    	    			rightPuls = 0;
    	    			printDuration = 0;*/
    	    			stop = true;
    	    			lcd.noBacklight();
    	    			lcd.clear();
    	    			lcd.print(F("EMERGENCY STOP"));
    	    			//lcd.print(TEXT_ID);
    	    			uiState = UISTATE_MAIN;
    	    			delay(1000);
    	    			//1 + A
    	    		}

    	    		if(bitMap[3] & 8) {
    	    			stop = false;
    	    			lcd.clear();
    	    			lcd.print(F("STOP RESET"));
    	    			//TODO watchdog test
    	    			//lcd.clear();
    	    			//lcd.print(F("WATCHDOG TEST"));
    	    			//while(true) {};
    	    			//1 + 3
    	    		}
    	}
    	/*
    	//TODO !!! Dirty trick !!!
    	if(bitMap[1] & 1) {
    		if(bitMap[0] == 2) rightDirMode=1;
    		if(bitMap[0] == 4) rightDirMode=2;
    		if(bitMap[0] == 8) rightDirMode=0;

    		if(bitMap[1] & 2) rightDirMode=1;
    		if(bitMap[1] & 4) rightDirMode=2;
    		if(bitMap[1] & 8) rightDirMode=0;

    		if(bitMap[2] == 2) {
    			leftPulMode=1;
    			return NO_KEY;
    		}
    		if(bitMap[2] == 4) leftPulMode=2;
    		if(bitMap[2] == 8) {
    			leftPulMode=0;
    			return NO_KEY;
    		}

    		//return NO_KEY;
    	}
    	*/

    	getKeys();
/*
		//TODO !!! Dirty trick !!!
		if(bitMap[3] == 8) {
					if(bitMap[0] == 8) {
						lcd.begin(LCD_COLS, LCD_ROWS);
						lcd.print(TEXT_ID);
						delay(500);
						//1 + A
					}
					if(bitMap[1] == 8) {
						lcd.clear();
						lcd.print(F("WATCHDOG TEST"));
						//while(true) {};
						//1 + 3
					}
		}
*/
		if(bitMap[3] == 4) {

			if(bitMap[2] == 8) uiPrintFilePause();
			if(bitMap[1] == 8) uiPrintFileStart();
			if(bitMap[0] == 8) uiPrintFileStop();

			if(bitMap[2] == 4) printMode=1;
			if(bitMap[1] == 4) printMode=2;
			if(bitMap[0] == 4) printMode=0;
			/*
			if(bitMap[2] == 2) rightPulMode=1;
			if(bitMap[1] == 2) rightPulMode=2;
			if(bitMap[0] == 2) rightPulMode=0;

			if(bitMap[2] == 1) rightDirMode=1;
			if(bitMap[1] == 1) rightDirMode=2;
			if(bitMap[0] == 1) rightDirMode=0;
			*/
		}

		if((bitMap[3] == 2 || bitMap[3] == 2 + 8) || uiState == UISTATE_CONTROL) {
			//7 +
			if(bitMap[3] == 8 || bitMap[3] == 8 + 2) leftGo(false, 100000 / pulSpeed);
			if(bitMap[2] == 8) leftGo(true, 100000 / pulSpeed);
			if(bitMap[1] == 8) rightGo(false, 100000 / pulSpeed);
	    	if(bitMap[0] == 8) rightGo(true, 100000 / pulSpeed);
	    	if(bitMap[2] == 1) printGo(100000 / pulSpeed);
		}

    	if(bitMap[0] || bitMap[1] || bitMap[2] || bitMap[3]) {
    		if(!kTime) {
    			kTime = millis();
    		}
    		if((kTime + 500) > millis()){
    			if((kTime + 200) < millis()) {
    				return NO_KEY;
    			}
    		}
    	}
        else
        	kTime = 0;

    	return getRawKey();
    }
};

byte rowPins[KPD_ROWS] = {0, 1, 2, 3}; //connect to the row pinouts of the keypad
byte colPins[KPD_COLS] = {4, 5, 6, 7}; //connect to the column pinouts of the keypad
Keypad_I2C2 kpd( makeKeymap(keys), rowPins, colPins, KPD_ROWS, KPD_COLS, KPD_I2CADDR, PCF8574 );

// Menu
#include "libraries/OMEEPROM/OMEEPROM.h"
#include "libraries/OMMenuMgr/OMMenuMgr.h"

class OMMenuMgr2 : public OMMenuMgr {

public:

    OMMenuMgr2(const OMMenuItem* c_first, uint8_t c_type, Keypad_I2C2* c_kpd) :OMMenuMgr( c_first, c_type) {
      kpd = c_kpd;
    };

    int OMMenuMgr2::_checkDigital() {
    	char k = kpd->getKey2();

    	if(k == 'A') return BUTTON_INCREASE;
    	if(k == 'B') return BUTTON_DECREASE;
    	if(k == 'D') return BUTTON_FORWARD;
    	if(k == '#') return BUTTON_BACK;
    	if(k == '*') return BUTTON_SELECT;

    	return k;
    	return BUTTON_NONE;
    }

private:

    Keypad_I2C2* kpd;
};

// Create a list of states and values for a select input
MENU_SELECT_ITEM  sel_auto= { 0, {"AUTO!"} };
MENU_SELECT_ITEM  sel_off = { 1, {"OFF!"} };
MENU_SELECT_ITEM  sel_on  = { 2, {"ON!"} };

MENU_SELECT_LIST  const state_list[] = { &sel_auto, &sel_off, &sel_on};
MENU_SELECT_LIST  const state_listOffOn[] = { &sel_off, &sel_on };
/*
MENU_SELECT rightDirMode_select = { &rightDirMode,           MENU_SELECT_SIZE(state_list),   MENU_TARGET(&state_list) };
MENU_VALUE rightDirMode_value =   { TYPE_SELECT,     0,     0,     MENU_TARGET(&rightDirMode_select), LIGHTMODE_ADDR };
MENU_ITEM rightDirMode_item =     { {"RIGHT DIR"}, ITEM_VALUE,  0,        MENU_TARGET(&rightDirMode_value) };
//                               TYPE             MAX    MIN    TARGET
MENU_SELECT rightPulMode_select =   { &rightDirMode,           MENU_SELECT_SIZE(state_list),   MENU_TARGET(&state_list) };
MENU_VALUE rightPulMode_value =     { TYPE_SELECT,     0,     0,     MENU_TARGET(&rightPulMode_select) , FANMODE_ADDR};
MENU_ITEM rightPulMode_item    =    { {"RIGHT PUL"}, ITEM_VALUE,  0,        MENU_TARGET(&rightPulMode_value) };

MENU_SELECT leftPulMode_select ={ &leftPulMode,           MENU_SELECT_SIZE(state_list),   MENU_TARGET(&state_list) };
MENU_VALUE leftPulMode_value =  { TYPE_SELECT,     0,     0,     MENU_TARGET(&leftPulMode_select), CYCLERMODE_ADDR };
MENU_ITEM leftPulMode_item    = { {"LEFT PUL"}, ITEM_VALUE,  0,        MENU_TARGET(&leftPulMode_value) };

MENU_SELECT leftDirMode_select ={ &leftDirMode,           MENU_SELECT_SIZE(state_list),   MENU_TARGET(&state_list) };
MENU_VALUE leftDirMode_value =  { TYPE_SELECT,     0,     0,     MENU_TARGET(&leftDirMode_select), CYCLERMODE_ADDR };
MENU_ITEM leftDirMode_item    = { {"LEFT DIR"}, ITEM_VALUE,  0,        MENU_TARGET(&leftDirMode_value) };
*/
MENU_SELECT printMode_select ={ &printMode,           MENU_SELECT_SIZE(state_list),   MENU_TARGET(&state_list) };
MENU_VALUE printMode_value =  { TYPE_SELECT,     0,     0,     MENU_TARGET(&printMode_select), PRINTMODE_ADDR };
MENU_ITEM printMode_item    = { {"PRINT OUTPUT"}, ITEM_VALUE,  0,        MENU_TARGET(&printMode_value) };

//MENU_LIST const submenu_list1[] = { &printMode_item, &leftPulMode_item, &leftDirMode_item, &rightPulMode_item, &rightDirMode_item,};
//MENU_ITEM menu_submenu1 =      { {"OUTPUTS->"},  ITEM_MENU,  MENU_SIZE(submenu_list1),  MENU_TARGET(&submenu_list1) };

MENU_VALUE distance_value={ TYPE_UINT,  0,    0,    MENU_TARGET(&distance), DISTANCE_ADDR };
MENU_ITEM distance_item   =			{ {"DISTANCE[mm]"},    ITEM_VALUE,  0,        MENU_TARGET(&distance_value) };

MENU_VALUE scale_value={ TYPE_UINT,  0,    0,    MENU_TARGET(&scale),SCALE_ADDR };
MENU_ITEM scale_item   =			{ {"SCALE[%]"},    ITEM_VALUE,  0,        MENU_TARGET(&scale_value) };

MENU_VALUE x0_value={ TYPE_UINT,  0,    0,    MENU_TARGET(&x0),X0_ADDR };
MENU_ITEM x0_item   =			{ {"X0[mm]"},    ITEM_VALUE,  0,        MENU_TARGET(&x0_value) };
MENU_VALUE y0_value={ TYPE_UINT,  0,    0,    MENU_TARGET(&y0),Y0_ADDR };
MENU_ITEM y0_item   =			{ {"Y0[mm]"},    ITEM_VALUE,  0,        MENU_TARGET(&y0_value) };

MENU_VALUE speed_value={ TYPE_UINT,  0,    0,    MENU_TARGET(&pulSpeed), SPEED_ADDR };
MENU_ITEM speed_item   =			{ {"SPEED"},    ITEM_VALUE,  0,        MENU_TARGET(&speed_value) };

MENU_VALUE printTime_value={ TYPE_UINT,  0,    0,    MENU_TARGET(&printTime), PRINTTIME_ADDR };
MENU_ITEM printTime_item   =			{ {"PRINT TIME[ms]"},    ITEM_VALUE,  0,        MENU_TARGET(&printTime_value) };

MENU_VALUE leftInitLength_value={ TYPE_UINT,  0,    0,    MENU_TARGET(&leftInitLength), LINIT_ADDR };
MENU_ITEM leftInitLength_item   =			{ {"INIT LENGTH[mm]"},    ITEM_VALUE,  0,        MENU_TARGET(&leftInitLength_value) };

MENU_VALUE rightDirInv_value={ TYPE_BYTE,  1,    0,    MENU_TARGET(&rightDirInv),RDIRINV_ADDR };
MENU_ITEM rightDirInv_item   =			{ {"RIGHT DIR INV"},    ITEM_VALUE,  0,        MENU_TARGET(&rightDirInv_value) };
MENU_VALUE leftDirInv_value={ TYPE_BYTE,  1,    0,    MENU_TARGET(&leftDirInv),LDIRINV_ADDR };
MENU_ITEM leftDirInv_item   =			{ {"LEFT DIR INV"},    ITEM_VALUE,  0,        MENU_TARGET(&leftDirInv_value) };
MENU_VALUE printInv_value={ TYPE_BYTE,  1,    0,    MENU_TARGET(&printInv),PRINTINV_ADDR };
MENU_ITEM printInv_item   =			{ {"PRINT INVERSION"},    ITEM_VALUE,  0,        MENU_TARGET(&printInv_value) };

MENU_LIST const submenu_list5[] = {&distance_item, &x0_item, &y0_item, &leftInitLength_item, &scale_item, &printTime_item, &speed_item, &leftDirInv_item, &rightDirInv_item, &printInv_item, &printMode_item};

MENU_ITEM menu_submenu5 = 			{ {"SETTINGS->"},  ITEM_MENU,  MENU_SIZE(submenu_list5),  MENU_TARGET(&submenu_list5) };

MENU_ITEM item_setClock   = 		{ {"SET CLOCK->"},  ITEM_ACTION, 0,        MENU_TARGET(&uiSetClock) };
//MENU_ITEM item_alarmList   = { {"ALARM LIST->"},  ITEM_ACTION, 0,        MENU_TARGET(&uiFileList) };

MENU_ITEM item_reset   = 			{ {"RESET DEFAULTS!"},  ITEM_ACTION, 0,        MENU_TARGET(&uiResetAction) };
//MENU_ITEM item_info   = { {"INFO->"},  ITEM_ACTION, 0,        MENU_TARGET(&uiInfo) };

MENU_ITEM item_control   = 			{ {"CALIBRATION"},  ITEM_ACTION, 0,        MENU_TARGET(&uiControl) };

MENU_ITEM printFilePause_control   ={ {"PRINT PAUSE!"},  ITEM_ACTION, 0,        MENU_TARGET(&uiPrintFilePause) };
MENU_ITEM printFileStart_control   ={ {"PRINT START!"},  ITEM_ACTION, 0,        MENU_TARGET(&uiPrintFileStart) };
MENU_ITEM printFileStop_control   = { {"PRINT STOP!"},  ITEM_ACTION, 0,        MENU_TARGET(&uiPrintFileStop) };

MENU_ITEM vpGoToXY0_control   = 	{ {"GOTO LEFTUP!"},  ITEM_ACTION, 0,        MENU_TARGET(&uiVpGoToXY0) };
MENU_ITEM vpGoToXY1_control   = 	{ {"GOTO RIGHTDOWN!"},  ITEM_ACTION, 0,        MENU_TARGET(&uiVpGoToXY1) };
MENU_ITEM vpGoToinit_control   = 	{ {"GOTO INIT!"},  ITEM_ACTION, 0,        MENU_TARGET(&uiVpGoToInit) };

MENU_VALUE fileIndex_value={ TYPE_UINT,  15,    0,    MENU_TARGET(&fileIndex), FILEINDEX_ADDR  };
MENU_ITEM fileIndex_item   =		{ {"SELECT FILE"},    ITEM_VALUE,  0,        MENU_TARGET(&fileIndex_value) };


//        List of items in menu level
MENU_LIST const root_list[]   = {  &printFilePause_control, &printFileStart_control, &printFileStop_control, &item_control, &vpGoToXY0_control, &vpGoToXY1_control, &vpGoToinit_control, &fileIndex_item, &menu_submenu5, &item_setClock, &item_reset};//&item_alarmList, &item_testme, , &item_info//&item_bazme, &item_bakme,

// Root item is always created last, so we can add all other items to it
MENU_ITEM menu_root     = { {"Root"},        ITEM_MENU,   MENU_SIZE(root_list),    MENU_TARGET(&root_list) };

OMMenuMgr2 Menu(&menu_root, MENU_DIGITAL, &kpd);


void serialPrintParInt(int address)
{
	int val;
	OMEEPROM::read(address, val);
	Serial.print(val);
	Serial.println();
	Serial.println();
}
void serialPrintParFloat(int address)
{
	float val;
	OMEEPROM::read(address, val);
	Serial.println(val);
	Serial.println();
	Serial.println();
}

void loadEEPROM() {
    using namespace OMEEPROM;

    read(PRINTMODE_ADDR, printMode);
    read(SPEED_ADDR, pulSpeed);
    read(FILEINDEX_ADDR, fileIndex);
    read(LINIT_ADDR, leftInitLength);
    read(DISTANCE_ADDR, distance);
    read(SCALE_ADDR, scale);
    read(PRINTTIME_ADDR, printTime);
    read(X0_ADDR, x0);
    read(Y0_ADDR, y0);
    read(LDIRINV_ADDR, leftDirInv);
    read(RDIRINV_ADDR, rightDirInv);
    read(PRINTINV_ADDR, printInv);
    //for(int i=0; i < 16; i++) {
    //     OMEEPROM::read(GSMNUMBER_ADDR + i, *(gsmNumber+i));
    //}
}

void saveDefaultEEPROM() {
	// save defaults
	printMode = 0;
	pulSpeed = 100;
	scale = 100;
	fileIndex = 2;
	distance = 3000;
	leftInitLength = 2500;
	printTime = 500;
	x0 = distance * 0.3;
	y0 = distance * 0.25;
	leftDirInv = 0;
	rightDirInv = 0;
	printInv = 0;

    using namespace OMEEPROM;
    write(PRINTMODE_ADDR, printMode);
    write(SPEED_ADDR, pulSpeed);
    write(FILEINDEX_ADDR, fileIndex);
    write(LINIT_ADDR, leftInitLength);
    write(DISTANCE_ADDR, distance);
    write(SCALE_ADDR, scale);
    write(PRINTTIME_ADDR, printTime);
    write(X0_ADDR, x0);
    write(Y0_ADDR, y0);
    write(LDIRINV_ADDR, leftDirInv);
    write(RDIRINV_ADDR, rightDirInv);
    write(PRINTINV_ADDR, printInv);
}

void printDirectory(File dir, int numTabs) {
  while (true) {

    File entry =  dir.openNextFile();
    if (! entry) {
    	break;
    }
    //for (uint8_t i = 0; i < numTabs; i++) {
    //	Serial.print('\t');
    //}
    //Serial.print(entry.name());

    if(fileNamesIndex < 16) {
    	strcpy((char *)fileNames[fileNamesIndex++], (const char*)entry.name());
    }

    if (entry.isDirectory()) {
    	//Serial.println("/");
    	printDirectory(entry, numTabs + 1);
    } else {
    	// files have sizes, directories do not
    	//Serial.print("\t\t");
    	//Serial.println(entry.size(), DEC);
    }
    entry.close();
  }
}



//////////////////////////////////
// setup
//////////////////////////////////

void setup() {

	digitalWrite(PRINT_PIN, true);
	pinMode(PRINT_PIN, OUTPUT);
	//digitalWrite(PRINT_PIN, true);

	// SD card shield SPI pin does not match Arduino Mega
	pinMode(10, INPUT);
	pinMode(11, INPUT);
	pinMode(12, INPUT);
	pinMode(13, INPUT);

	Serial.begin(9600);
	while(!Serial);
	Serial.println(TEXT_ID);


	//setup2();
	Wire.begin( );
	kpd.begin( makeKeymap(keys) );
	lcd.begin(LCD_COLS, LCD_ROWS);

	lcd.print(TEXT_ID);

    if (!SD.begin(SS)) {
    	Serial.println(F("SD FAILED!"));
    	lcd.clear();
    	lcd.backlight();
    	lcd.print(F("SD FAILED!"));
    	lcd.setCursor(0, 1);
    	lcd.print(F("PRESS KEY"));
    	while(!kpd.getRawKey());
    	lcd.noBacklight();
    	//return;
    }
    else
    	sd = true;
    if(sd) {
    	  file = SD.open("/");
    	  printDirectory(file, 0);
    }
    file.close();

	if( OMEEPROM::saved() )
		loadEEPROM();
	else
		saveDefaultEEPROM();

	vp.setSize(distance, x0, y0);

	pulSpeed= max(100, pulSpeed);
	Timer3.initialize(pulSpeed); // set a timer of length 100000 microseconds (or 0.1 sec - or 10Hz => the led will blink 5 times, 5 cycles of on-and-off, per second)
	Timer3.attachInterrupt( timerIsr ); // attach the service routine here
	//Timer1.setPeriod();



#ifdef __RTC__
	rtc.begin();
	if (rtc.lostPower()) {
		Serial.println(F("RTC LOST POWER!"));
		// following line sets the RTC to the date & time this sketch was compiled
		rtc.adjust(DateTime(F(__DATE__), F(__TIME__)));
	}

	now = rtc.now();
#endif

	milliseconds = millis();

	//TODO: refresh display
	//uiMain();
	Menu.setDrawHandler(uiDraw);
	Menu.setExitHandler(uiMain);
	Menu.enable(true);

	//pinMode(LED_PIN, OUTPUT);
	pinMode(PRINT_PIN, OUTPUT);
	pinMode(R_PUL_PIN, OUTPUT);
	pinMode(R_DIR_PIN, OUTPUT);
	pinMode(L_PUL_PIN, OUTPUT);
	pinMode(L_DIR_PIN, OUTPUT);

	vpInit();

	//wdt_enable(WDTO_8S);
}

bool getInstrumentControl(bool a, byte mode) {
	mode = mode & 3;
	if(mode == 0) return a;
	if(mode == 1) return false;
	if(mode == 2) return true;
	return false;
}

double analogRead(int pin, int samples){
  int result = 0;
  for(int i=0; i<samples; i++){
    result += analogRead(pin);
  }
  return (double)(result / samples);
}



void vpInit() {
	vp.setSize(3000);
	leftPulsPos = vp.getStepsTo(2500, 0);
	rightPulsPos = vp.getStepsTo(2500, 0);
}

void vpScrollTo(unsigned long l, unsigned long r) {
	//TODO: directions
	leftDirAuto = vp.getDirection(l, vp.getLength(leftPulsPos));
	rightDirAuto = vp.getDirection(r, vp.getLength(rightPulsPos));

	leftPuls = vp.getStepsTo(l, vp.getLength(leftPulsPos));
	rightPuls = vp.getStepsTo(r, vp.getLength(rightPulsPos));
/*
	Serial.print(vp.getLength(leftPulsPos));
	Serial.print('\t');
	//Serial.print(l - vp.getLength(leftPulsPos));
	//Serial.print('\t');
	Serial.print(vp.getDirection(l, vp.getLength(leftPulsPos)));
	Serial.print('\t');
	Serial.print(vp.stepDistance);
	Serial.print('\t');
	Serial.println(leftPuls);
*/

}

void vpGoToXY(int x, int y) {
	//double l = vp.getLl(x, y);
	//double r = vp.getRl(x, y);
	vpScrollTo(vp.getLl(x, y), vp.getRl(x, y));

}


//////////////////////////////////
// main loop
//////////////////////////////////

bool bPrint;

void loop() {

	//wdt_reset();

#ifdef __RTC__
	now = rtc.now();
#endif


	//microseconds = micros();
	milliseconds = millis();

	if(millisecondsPrev + 1000 < milliseconds || milliseconds < millisecondsPrev) {
		secondsCounter++;

		if (secondsCounter % 2 == 0) {
		}
		secToggle ? secToggle = false : secToggle = true;
		millisecondsPrev = millis();
	}

	if (!Menu.shown()) {
		if(!uiState) {
			//TODO: refreash display
			//uiMain();
		}
	}
	char key = kpd.getKey2();
	if(key == '#') {
			uiState = 0;
			uiPage = 0;
			Menu.enable(true);

			if(!Menu.shown()) {
				uiMain();
			}
	}
	else if(!Menu.shown() || !Menu.enable()) {

		if(key == '8') {
			uiControl();
		}
		else if(key == '9') {
			uiInfo();
		}
		if(key == 'C') {
			uiFileList();
		}

		else {
			uiScreen();
		}

	}
	Menu.checkInput();


	if(state == STATE_RUNNING) {
		if((leftPuls == 0) && (rightPuls == 0) && (printDuration == 0)) {
			if(bPrint) {
				bPrint = false;
				printGo(printTime);
				Serial.print(vp.getX(vp.getLength(leftPulsPos), vp.getLength(rightPulsPos)));
				Serial.print('\t');
				Serial.print(vp.getY(vp.getLength(leftPulsPos), vp.getLength(rightPulsPos)));
				Serial.print('\t');
				Serial.print(vp.getLength(leftPulsPos));
				Serial.print('\t');
				Serial.print(vp.getLength(rightPulsPos));
				Serial.println('\t');

			}
			else if(file) {
				if(file.available()) {
					int x=0;
					x = file.read();
					x += file.read() << 8;
					x += file.read() << 16;
					x += file.read() << 24;
					x = (x * scale) / 100;
					//Serial.print(i);
					//Serial.print('\t');
					int y=0;
					y = file.read();
					y += file.read() << 8;
					y += file.read() << 16;
					y += file.read() << 24;
					y = (y * scale) / 100;
					//Serial.print(i);
					//Serial.print('\t');
					int p=0;
					p = file.read();
					p += file.read() << 8;
					p += file.read() << 16;
					p += file.read() << 24;
					//Serial.print(i);
					//Serial.println('\t');
					//TODO: check
					if((vp.getLength(leftPulsPos) + vp.getLength(rightPulsPos) + 1000) < distance) {
						lcd.clear();
						lcd.print(F("TOO SHORT ROPE!"));
						state = STATE_STOPPED;
						while(key != '#') {
							kpd.getKey2();
						}

					}
					vpGoToXY(x, y);
					bPrint = true;

				}
				else {
					state = STATE_DONE;
					file.close();
				}
			}
		}
	}


	//////////////////////////////////
	// outputs
	//////////////////////////////////

	/*
	//TODO: Interrupt driven
	//if(cycles >= cyclesPrev + pulSpeed) {
	if(microseconds >= microsecondsPrev + pulSpeed) {
		//cyclesPrev = cycles;
		microsecondsPrev = microseconds;
		if(rightPuls) {
			rightPuls--;
			rightPulAuto = !rightPulAuto;

			if(rightDirAuto)
				rightPulsPos++;
			else
				rightPulsPos--;
		}
		if(leftPuls) {
			leftPuls--;
			leftPulAuto = !leftPulAuto;

			if(leftDirAuto)
				leftPulsPos++;
			else
				leftPulsPos--;
		}

		if(printDuration) {
			printDuration--;
			printAuto = true;
		}
		else
			printAuto = false;

	}
	//cycles++;
	*/


	/*
	printControl = getInstrumentControl(printAuto, printMode);
	rightPulControl = getInstrumentControl(rightPulAuto, rightPulMode);
    rightDirControl = getInstrumentControl(rightDirAuto, rightDirMode);
	leftPulControl = getInstrumentControl(leftPulAuto, leftPulMode);
	leftDirControl = getInstrumentControl(leftDirAuto, leftDirMode);
	*/
	/*
	if(kpd.getRawKey()) {
		// key pressed
	}
	*/

	/*
	//digitalWrite(LED_PIN, !printControl);
	digitalWrite(PRINT_PIN, !printControl);
	digitalWrite(R_DIR_PIN, !rightDirControl);
	digitalWrite(R_PUL_PIN, !rightPulControl);
	digitalWrite(L_DIR_PIN, !leftDirControl);
	digitalWrite(L_PUL_PIN, !leftPulControl);
	 */


	/*
	pinMode(LED_PIN, OUTPUT);
	pinMode(PRINT_PIN, OUTPUT);
	pinMode(R_PUL_PIN, OUTPUT);
	pinMode(R_DIR_PIN, OUTPUT);
	pinMode(L_PUL_PIN, OUTPUT);
	pinMode(L_DIR_PIN, OUTPUT);
	*/

	//////////////////////////////////
	// communication
	//////////////////////////////////
  	if (Serial.available() > 0) {
  		String text = Serial.readString();
  		int pos;
  		//Serial.println(text);

  		//parseCmd(text, MESSAGE_CMD_LIGHT, rightDirMode);
  		//parseCmd(text, MESSAGE_CMD_FAN, rightDirMode);
  		//parseCmd(text, MESSAGE_CMD_CYCLER, leftPulMode);

  		pos = text.indexOf(MESSAGE_CMD_PARREADINT);
  		if (pos >= 0) {
  			serialPrintParInt(text.substring(pos + strlen(MESSAGE_CMD_PARREADINT)).toInt());
  		}
  		pos = text.indexOf(MESSAGE_CMD_PARREADFLOAT);
  		if (pos >= 0) {
  			serialPrintParFloat(text.substring(pos + strlen(MESSAGE_CMD_PARREADFLOAT)).toFloat());
  		}
  		pos = text.indexOf(MESSAGE_CMD_PARWRITEINT);
  		if (pos >= 0) {
  			int address = text.substring(pos + strlen(MESSAGE_CMD_PARWRITEINT)).toInt();
  			//#PWI0125:25
  			int value = text.substring(pos + strlen(MESSAGE_CMD_PARWRITEINT) + 5).toInt();
  			OMEEPROM::write(address, value);
  		}
  		pos = text.indexOf(MESSAGE_CMD_PARWRITEFLOAT);
  		if (pos >= 0) {
  			int address = text.substring(pos + strlen(MESSAGE_CMD_PARWRITEINT)).toInt();
  			//#PWI0125:25
  			float value = text.substring(pos + strlen(MESSAGE_CMD_PARWRITEINT) + 5).toFloat();
  			OMEEPROM::write(address, value);
  		}
  		pos = text.indexOf(MESSAGE_CMD_PARRELOAD);
  		if (pos >= 0) {
  			loadEEPROM();
  		}

		if (text.indexOf(MESSAGE_CMD_REQUEST)!=-1 ) {
			/*
			Serial.println();

			rightDirControl = getInstrumentControl(rightDirAuto, rightDirMode);
			rightDirControl = getInstrumentControl(rightDirAuto, rightDirMode);
			leftPulControl = getInstrumentControl(leftPulAuto, leftPulMode);

			Serial.print(MESSAGE_LIGHT_CONTROL);
			rightDirControl ? Serial.print('1') : Serial.print('0');
			rightDirMode ? Serial.println('M') : Serial.println('A');
			Serial.print(MESSAGE_FAN_CONTROL);
			rightDirControl ? Serial.print('1') : Serial.print('0');
			rightDirMode ? Serial.println('M') : Serial.println('A');
			Serial.print(MESSAGE_CYCLER_CONTROL);
			leftPulControl ? Serial.print('1') : Serial.print('0');
			leftPulMode ? Serial.println('M') : Serial.println('A');
			Serial.println();

  			Serial.print(MESSAGE_TEMP);
  			Serial.println(temperature);
  			Serial.print(MESSAGE_EXT);
  			//Serial.print(digitalRead(EXT_PIN));
  			Serial.println(external);
  			Serial.print(MESSAGE_POWER);
  			Serial.println(power);

  			Serial.print(MESSAGE_GSM);
  			Serial.print(gsmMode);
  			Serial.print(' ');
  			Serial.print(gsmNumber);
  			Serial.print(' ');
  			Serial.print(gsmCode);

  			Serial.println();
  			Serial.println();

  			Serial.println();
  			char msg[MESSAGELENGTH + 1];
  			for(int i = 0; i< MESSAGESCOUNT; i++) {
  				readMessage(i, (byte*)msg);
  				Serial.println(msg);
  			}
			*/
  			Serial.println();
  			Serial.println();
   		}
  	}
}

void uiOK(){
	lcd.clear();
	lcd.setCursor(0, 0);
	lcd.print(F("OK"));
	delay(OK_DELAY);
}

void uiResetAction() {
	saveDefaultEEPROM();
	uiOK();
}

void uiDraw(char* p_text, int p_row, int p_col, int len) {
	lcd.backlight();
	lcd.setCursor(p_col, p_row);
	for( int i = 0; i < len; i++ ) {
		if( p_text[i] < '!' || p_text[i] > '~' )
			lcd.write(' ');
		else
			lcd.write(p_text[i]);
	}
}

void uiInstrument(bool instrument, byte mode) {
	lcd.print(instrument);
	if(mode == 0)
		lcd.print('A');
	else if(mode < 3)
		lcd.print('M');
	else
		lcd.print('X');
}

// User interface menu functions
void uiFileList() {
	lcd.backlight();
	Menu.enable(false);
	uiState = UISTATE_FILELIST;
	uiPage=0;
	uiKeyTime =0;
	uiKeyPressed = 0;
	lcd.clear();
}

void uiPrintFilePause() {
	Menu.enable(false);
	uiState = UISTATE_INFO;
	uiPage = 0;
	uiKeyTime = 0;
	uiKeyPressed = 0;

	//lcd.clear();
	//lcd.setCursor(0, 0);
			  //"0123456789ABCDEF"
	//lcd.print(F("PRINTING PAuSED"));
	//uiLcdPrintSpaces8();

	state = STATE_PAUSED;
}

void uiPrintFileStop() {
	Menu.enable(false);
	uiState = UISTATE_INFO;
	uiPage = 0;
	uiKeyTime = 0;
	uiKeyPressed = 0;

	//lcd.clear();
	//lcd.setCursor(0, 0);
			  //"0123456789ABCDEF"
	//lcd.print(F("PRINTING STOPPED"));
	//uiLcdPrintSpaces8();

	state = STATE_STOPPED;

	if(file)
		file.close();
}

void uiPrintFileStart() {

	lcd.noBacklight();

	Menu.enable(false);
	uiPage=0;
	uiKeyTime =0;
	uiKeyPressed = 0;
	//lcd.clear();
	//lcd.setCursor(0, 0);
			  //"0123456789ABCDEF"
	//lcd.print(F("F: "));
	//lcd.print(fileNames[fileIndex]);

	//lcd.setCursor(0, 1);
	if(!file)
		file = SD.open(fileNames[fileIndex]);

	if (file) {
		//uiState = UISTATE_PRINTING;
		uiState = UISTATE_INFO;
		uiPage = 0;
		state = STATE_RUNNING;
	}
	else {
		lcd.print(F("FILE ERROR!"));
	}
	//file.close();
}

void uiControl() {
	lcd.backlight();
	Menu.enable(false);
	uiState = UISTATE_CONTROL;
	uiPage = 1;
	uiKeyTime = 0;
	uiKeyPressed = 0;

	lcd.clear();
	lcd.setCursor(0, 0);
			  //"0123456789ABCDEF"
	lcd.print(F("CALIBR *ENT #ESC"));
	lcd.setCursor(0, 1);
			  //"0123456789ABCDEF"
	lcd.print(F("1U 2D  0P  3D AU"));

}

void uiInfo() {
	lcd.backlight();
	Menu.enable(false);
	uiState = UISTATE_INFO;
	uiPage=0;
	uiKeyTime =0;
	uiKeyPressed = 0;
	lcd.clear();
}

void uiSetClock() {
	Menu.enable(false);
	uiState = UISTATE_SETCLOCK;
#ifdef __RTC__
	nowSetClock = rtc.now();
#endif

	uiPage=0;
	uiKeyTime = 0;
	uiKeyPressed = 0;
	lcd.clear();
}

void uiVpGoToXY0() {
	uiOK();
	vpGoToXY(0, 0);
}
void uiVpGoToXY1() {
	uiOK();
	vpGoToXY(vp.X_SIZE, vp.Y_SIZE);
}

void uiVpGoToInit() {
	uiOK();
	vpScrollTo(2500, 2500);
}

void uiScreen() {
	//Menu.enable(false);
	//lcd.backlight();

	char key = kpd.getRawKey();
	// First key stroke after delay, then pause and then continuously
	if(key) {
		 if(!uiKeyTime) {
			 uiKeyTime = milliseconds;
		 }

		 if((uiKeyTime + 120) > milliseconds) {
			 key = 0;
		 }
		 else {
			 if(uiKeyPressed) {
				 key = 0;
			 }
			 else {
				 uiKeyPressed = key;
			 }
		 }

		 if((uiKeyTime + 600) < milliseconds){
			 uiKeyPressed = 0;
		 }
	}
	else {

		uiKeyTime = 0;
		uiKeyPressed = 0;
	}


	if(uiState == UISTATE_CONTROL) {
		if(key == KPD_ENTER) {
			uiOK();

			vpInit();
			uiState = UISTATE_MAIN;
			Menu.enable(true);
		}
	}

	if(uiState == UISTATE_INFO) {

		if(key == KPD_UP) {
			uiPage--;
			//lcd.clear();
		}
		if(key == KPD_DOWN) {
			uiPage++;
			//lcd.clear();
		}
		uiPage = max(0, uiPage);
		uiPage = min(6, uiPage);

		if(uiPage == 0) {
			//TODO: once per ?
			//lcd.clear();
			lcd.setCursor(0, 0);
			if(state == STATE_STOPPED ) {
			    lcd.print(F("PRINTIG STOPPED"));
			    uiLcdPrintSpaces8();
			    lcd.setCursor(0, 1);
			    uiLcdPrintSpaces8();
			    uiLcdPrintSpaces8();
			}
			else if(state == STATE_RUNNING || state == STATE_PAUSED) {
				if(state == STATE_PAUSED )
				    lcd.print(F("PRINTIG PAUSED"));
				else
					lcd.print(F("PRINTIG RUNNING"));
			    uiLcdPrintSpaces8();
			    lcd.setCursor(0, 1);
				lcd.print(file.position()/12);
				lcd.print('/');
				lcd.print(file.size()/12);
			    uiLcdPrintSpaces8();
			    uiLcdPrintSpaces8();
				//file.read();
			}
			/*
			else if(state == STATE_PAUSED ) {
			    lcd.print(F("PRINTIG PAUSED"));
			    uiLcdPrintSpaces8();
			    lcd.setCursor(0, 1);
			    uiLcdPrintSpaces8();
			    uiLcdPrintSpaces8();
			}
			*/
			else if(state == STATE_DONE ) {
			    lcd.print(F("PRINTIG DONE"));
			    uiLcdPrintSpaces8();
			    lcd.setCursor(0, 1);
			    uiLcdPrintSpaces8();
			    uiLcdPrintSpaces8();
			}
		}
		if(uiPage == 1) {
			lcd.setCursor(0, 0);
			//lcd.print(F("PRINTIG DONE"));
			lcd.print(vp.getLength(leftPulsPos));
		    uiLcdPrintSpaces8();

		    lcd.setCursor(8, 0);
		    lcd.print(vp.getLength(rightPulsPos));
		    uiLcdPrintSpaces8();

		    lcd.setCursor(0, 1);
		    lcd.print(leftPulsPos);
		    uiLcdPrintSpaces8();
		    lcd.setCursor(8, 1);
		    lcd.print(rightPulsPos);
		    uiLcdPrintSpaces8();

		}

		if(uiPage == 2) {
			if(false) {
				secToggle ? lcd.backlight() : lcd.noBacklight();
			}
			else {
				lcd.backlight();
			}

			lcd.setCursor(0, 0);
			// Message
			lcd.print("PR");
			uiInstrument(printControl, printMode);
			uiLcdPrintSpaces8();
			uiLcdPrintSpaces8();


			lcd.setCursor(10, 0);
			lcd.print(' ');
			if (now.hour() < 10)
				lcd.print('0');
			lcd.print(now.hour(), DEC);
			if(secToggle) {
				lcd.print(':');
			}
			else
				lcd.print(' ');
			if (now.minute() < 10)
				lcd.print('0');
			lcd.print(now.minute(), DEC);


			lcd.setCursor(0, 1);
			lcd.print("LP");
			uiInstrument(leftPulControl, leftPulMode);
			lcd.print("LD");
			uiInstrument(leftDirControl, leftDirMode);
			lcd.print("RP");
			uiInstrument(rightPulControl, rightPulMode);
			lcd.print("RD");
			uiInstrument(rightDirControl, rightDirMode);
		}
		if(uiPage == 3) {
		    lcd.setCursor(0, 0);
			lcd.print(F("DIST[mm]:"));
			lcd.print(distance);
			uiLcdPrintSpaces8();
			lcd.setCursor(0, 1);
			lcd.print(F("INIT[mm]:"));
			lcd.print(leftInitLength);
			uiLcdPrintSpaces8();
		}
		if(uiPage == 4) {
			lcd.setCursor(0, 0);
			lcd.print(F("X0[mm]:"));
			lcd.print(x0);
			uiLcdPrintSpaces8();
			lcd.setCursor(0, 1);
			lcd.print(F("Y0[mm]:"));
			lcd.print(y0);
			uiLcdPrintSpaces8();
		}
		if(uiPage == 5) {
		    lcd.setCursor(0, 0);
			lcd.print(F("SPEED[]:"));
			lcd.print(pulSpeed);
			uiLcdPrintSpaces8();
			lcd.setCursor(0, 1);
			lcd.print(F("PRINT T[ms]:"));
			lcd.print(printTime);
			uiLcdPrintSpaces8();
		}
		if(uiPage == 6) {
		    lcd.setCursor(0, 0);
			lcd.print(F("SCALE[%]:"));
			lcd.print(scale);
			uiLcdPrintSpaces8();
			lcd.setCursor(0, 1);
			lcd.print(F("FILE:"));
			lcd.print(fileNames[fileIndex]);
			uiLcdPrintSpaces8();
			uiLcdPrintSpaces8();
		}
	}

	if(uiState == UISTATE_FILELIST) {
		if(key == KPD_UP)
			uiPage--;
		if(key == KPD_DOWN)
			uiPage++;


		//char msg[MESSAGELENGTH + 1];
		uiPage = min(uiPage, 14);
		uiPage = max(uiPage, 0);
		lcd.setCursor(0, 0);
		lcd.print(uiPage);
		lcd.print(F(": "));
		//readMessage(uiPage, (byte*)msg);
		//lcd.print(msg);
		lcd.print(fileNames[uiPage]);
		uiLcdPrintSpaces8();
		uiLcdPrintSpaces8();
		lcd.setCursor(0, 1);
		lcd.print(uiPage + 1);
		lcd.print(F(": "));

		//readMessage(uiPage + 1, (byte*)msg);
		//lcd.print(msg);
		lcd.print(fileNames[uiPage + 1]);
		uiLcdPrintSpaces8();
		uiLcdPrintSpaces8();


	}

	if(uiState == UISTATE_SETCLOCK) {
		//	uiPage--;
		if(key == KPD_RIGHT)
			uiPage++;

		lcd.setCursor(0,0);
				  //"0123456789ABCDEF"
		lcd.print(F("SET CLOCK"));
		Serial.println("SET CLOCK");

		uiPage = max(0, uiPage);
		uiPage = min(4, uiPage);

		uint8_t hh = nowSetClock.hour();
		uint8_t mm = nowSetClock.minute();
		uint8_t d = nowSetClock.day();
		uint8_t m = nowSetClock.month();
		uint16_t y = nowSetClock.year();

		lcd.setCursor(11,0);
		if(uiPage==0) {
			if(key==KPD_UP)hh++;
			if(key==KPD_DOWN)hh--;
					  //"0123456789ABCDEF"
			lcd.print(F(" HOUR"));
		}

		if(uiPage==1) {
			if(key==KPD_UP)mm++;
			if(key==KPD_DOWN)mm--;
			lcd.print(F("  MIN"));
		}

		if(uiPage==2) {
			if(key==KPD_UP)d++;
			if(key==KPD_DOWN)d--;
			lcd.print(F("  DAY"));
		}

		if(uiPage==3) {
			if(key==KPD_UP)m++;
			if(key==KPD_DOWN)m--;
			lcd.print(F("MONTH"));
		}

		if(uiPage==4) {
			if(key==KPD_UP)y++;
			if(key==KPD_DOWN)y--;
			lcd.print(F(" YEAR"));
		}

		hh = min(23, hh);
		hh = max(0, hh);
		mm = min(59, mm);
		mm = max(0, mm);
		d = min(31, d);
		d = max(1, d);
		m = min(12, m);
		m = max(1, m);
		y = min(9999, y);
		y = max(2000, y);

		nowSetClock = DateTime(y, m, d, hh, mm, 0);

		lcd.setCursor(0,1);
		if(hh<10)
			lcd.print('0');
		lcd.print(hh);
		lcd.print(':');
		if(mm<10)
			lcd.print('0');
		lcd.print(mm);
		lcd.print(' ');

		if(d<10)
			lcd.print('0');
		lcd.print(d);
		lcd.print('/');
		if(m<10)
			lcd.print('0');
		lcd.print(m);
		lcd.print('/');
		//if(y<10)
		//	lcd.print('0');
		lcd.print(y);

		//!!!TODO
		if(key == KPD_ENTER) {
#ifdef __RTC__
			rtc.adjust(nowSetClock);
#endif
			Menu.enable(true);
		}
	}

	if(uiState == UISTATE_EDITTEXT) {
		/*
		lcd.setCursor(0, 0);
		//"0123456789ABCDEF"
		if(key == 'C')
			uiPage++;
		if(key == 'D')
			uiPage--;

		uiPage = max(0, uiPage);
		uiPage = min(15, uiPage);

		//text[0] = 64;
		uint8_t i;
		//strncpy(text2, text, 16);
		i = tmp_text[uiPage];
		if(key == KPD_UP) i++;
		if(key == KPD_DOWN) i--;
		i = max(32, i);
		i = min(126, i);
		tmp_text[uiPage] = (char)i;

		lcd.setCursor(0, 1);
		lcd.print(tmp_text);

		uiLcdPrintSpaces8();
		uiLcdPrintSpaces8();

		if(secToggle) {
			lcd.setCursor(uiPage, 1);
			lcd.print('_');
		}

		if(key == KPD_ENTER) {
			tmp_text[uiPage+1] = 0;
			for(int i=uiPage+2; i<16; i++)
				tmp_text[i]=255;

			//TODO: 15 or 16 chars?
			tmp_text[16] = 0;
			//Serial.println(tmp_text);
			strncpy(text, tmp_text, 16);

			Menu.enable(true);
		}
		*/
	}
}

/*
void uiInfo() {
	//"123456789ABCDEF"
	lcd.clear();
	lcd.setCursor(0, 0);
	lcd.print(F("BCSEDLON@"));
	lcd.setCursor(0, 1);
	lcd.print(F("GMAIL.COM"));
	Menu.enable(false);
}
*/

void uiLcdPrintAlarm(bool alarmHigh, bool alarmLow) {
	if(alarmHigh)
		lcd.print('+');
	else if(alarmLow)
		lcd.print('-');
	else
		lcd.print(' ');
}

void uiLcdPrintSpaces8() {
	lcd.print(F("        "));
}

void uiMain() {

	if(pulSpeed != pulSpeedPrev) {
		pulSpeed= max(100, pulSpeed);
		Timer3.setPeriod(pulSpeed);
		pulSpeedPrev = pulSpeed;
	}
	/*if(distance != distancePrev) {
		distancePrev = distance;
		vp.setSize(distance);

	}*/
	vp.setSize(distance, x0, y0);
	Serial.print(vp.X_SIZE);
	Serial.print('\t');
	Serial.print(vp.X_0);
	Serial.print('\t');
	Serial.println(vp.Y_0);

	lcd.noBacklight();
	lcd.clear();
	lcd.print(TEXT_ID);
	//uiState = UISTATE_INFO;

	//uiState = UISTATE_MAIN;
	/*
	if(false) {
		secToggle ? lcd.backlight() : lcd.noBacklight();
	}
	else {
		lcd.backlight();
	}

	lcd.setCursor(0, 0);
	// Message
	lcd.print("PR");
	uiInstrument(printControl, printMode);


	lcd.setCursor(10, 0);
	lcd.print(' ');
	if (now.hour() < 10)
		lcd.print('0');
	lcd.print(now.hour(), DEC);
	if(secToggle) {
		lcd.print(':');
	}
	else
		lcd.print(' ');
	if (now.minute() < 10)
		lcd.print('0');
	lcd.print(now.minute(), DEC);


	lcd.setCursor(0, 1);
	lcd.print("LP");
	uiInstrument(leftPulControl, leftPulMode);
	lcd.print("LD");
	uiInstrument(leftDirControl, leftDirMode);
	lcd.print("RP");
	uiInstrument(rightPulControl, rightPulMode);
	lcd.print("RD");
	uiInstrument(rightDirControl, rightDirMode);
	*/
	/*
	lcd.print(' ');
	if(abs(temperature) < 10)
	lcd.print('0');
	lcd.print(temperature);
	lcd.setCursor(20, 1);
	lcd.print('C');
	*/
}

void leftGo(bool dir, unsigned int puls) {
	leftDirAuto = dir;
	leftPuls = puls;
}

void rightGo(bool dir, unsigned int puls) {
	rightDirAuto = !dir;
	rightPuls = puls;
}

void printGo(unsigned int duration) {
	printDuration = duration;
}

/// --------------------------
/// Custom ISR Timer Routine
/// --------------------------
void timerIsr()
{
	if(stop) {
		digitalWrite(PRINT_PIN, !printAuto);
		return;
	}

	if(rightPuls) {
		rightPuls--;
		rightPulAuto = !rightPulAuto;

		if(rightDirAuto)
			rightPulsPos++;
		else
			rightPulsPos--;
	}
	if(leftPuls) {
		leftPuls--;
		leftPulAuto = !leftPulAuto;

		if(leftDirAuto)
			leftPulsPos++;
		else
			leftPulsPos--;
	}


	//microseconds = micros();
	//if(microseconds >= microsecondsPrev + printTime * 1000) {
	//	microsecondsPrev = microseconds;
		//TODO:
		if(printDuration) {
			printDuration--;
			printAuto = true;
		}
		else
			printAuto = false;
	//}


	printControl = getInstrumentControl(printAuto, printMode);
	digitalWrite(PRINT_PIN, printInv? printAuto : !printAuto);
	digitalWrite(R_DIR_PIN, rightDirInv? rightDirAuto : !rightDirAuto);
	digitalWrite(R_PUL_PIN, !rightPulAuto);
	digitalWrite(L_DIR_PIN, leftDirInv? leftDirAuto: !leftDirAuto);
	digitalWrite(L_PUL_PIN, !leftPulAuto);


}
