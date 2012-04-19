/* Name: set-led.c
 * Project: hid-custom-rq example
 * Author: Christian Starkjohann, modified by Herrchen
 * Creation Date: 2008-04-10
 * Tabsize: 4
 * Copyright: (c) 2008 by OBJECTIVE DEVELOPMENT Software GmbH
 * License: GNU GPL v2 (see License.txt), GNU GPL v3 or proprietary (CommercialLicense.txt)
 * This Revision: $Id: set-led.c 692 2008-11-07 15:07:40Z cs $
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>
#include <usb.h>
#include "opendevice.h" /* common code moved to separate module */

/* Taken from original firmware/request.h */
#define CUSTOM_RQ_SET_RED    3
#define CUSTOM_RQ_SET_GREEN  4
#define CUSTOM_RQ_SET_BLUE   5

#define CLAMP(x, low, high)  (((x) > (high)) ? (high) : (((x) < (low)) ? (low) : (x)))

/* Taken from original firmware/usbconfig.h */
#define USB_CFG_VENDOR_ID   0xc0, 0x16
#define USB_CFG_DEVICE_ID   0xdf, 0x05
#define USB_CFG_VENDOR_NAME 'd', 'a', 'v', 'e', '.', 'h'
#define USB_CFG_DEVICE_NAME 'L', 'E', 'D', 'C', 't', 'l', 'H', 'I', 'D'

static void usage(char *name)
{
    fprintf(stderr, "usage:\n");
    fprintf(stderr, "  %s on ....... turn on LED\n", name);
    fprintf(stderr, "  %s off ...... turn off LED\n", name);
    fprintf(stderr, "  %s cat ...... read rgb tuples from stdin\n", name);
    fprintf(stderr, "  %s rgb r g b  Set LED color to r,g,b\n", name);
}

//////////////////////////////////

static void set_rgb(usb_dev_handle * handle, int r, int g, int b)
{
    char buffer[4] =  {0,0,0,0};
    int flags = USB_TYPE_VENDOR | USB_RECIP_DEVICE | USB_ENDPOINT_OUT;
    usb_control_msg(handle, flags, CUSTOM_RQ_SET_RED,   r, 0, buffer, 0, 5000);
    usb_control_msg(handle, flags, CUSTOM_RQ_SET_GREEN, g, 0, buffer, 0, 5000);
    usb_control_msg(handle, flags, CUSTOM_RQ_SET_BLUE,  b, 0, buffer, 0, 5000);
}

//////////////////////////////////

static int string_to_col(const char * arg)
{
    return CLAMP(strtol(arg,NULL,10),0,255);
}

//////////////////////////////////

static void set_rgb_from_arr(usb_dev_handle * handle, const char ** arr)
{
    int r,g,b;
    r = string_to_col(arr[0]); 
    g = string_to_col(arr[1]); 
    b = string_to_col(arr[2]); 

    set_rgb(handle,r,g,b);
}

//////////////////////////////////

int main(int argc, char **argv)
{
    usb_dev_handle *handle = NULL;
    const unsigned char rawVid[2] = {USB_CFG_VENDOR_ID};
    const unsigned char rawPid[2] = {USB_CFG_DEVICE_ID};
    char vendor[] = {USB_CFG_VENDOR_NAME, 0};
    char product[] = {USB_CFG_DEVICE_NAME, 0};
    int vid, pid;

    usb_init();

    if(argc < 2)
    {
        usage(argv[0]);
        exit(1);
    }

    /* compute VID/PID from usbconfig.h so that there is a central source of information */
    vid = rawVid[1] * 256 + rawVid[0];
    pid = rawPid[1] * 256 + rawPid[0];
    /* The following function is in opendevice.c: */
    if(usbOpenDevice(&handle, vid, vendor, pid, product, NULL, NULL, NULL) != 0)
    {
        fprintf(stderr, "Could not find USB device \"%s\" with vid=0x%x pid=0x%x\n", product, vid, pid);
        exit(1);
    }

    if(strcasecmp(argv[1], "cat") == 0)
    {
        const int size = 1024;
        char buf[size+1];
        const char * rgb[3] = {0,0,0};
        int i = 0;

        for(;;)
        {
            bool is_valid = true;

            memset(buf,0,size);
            if(fgets(buf,size,stdin) == NULL)
            {
                puts("Got EOF, quitting");
                break;
            }

            /* Split stdin argument of form '255 0 127' */
            char * node = buf;
            for(i = 0; i < 3; i++)
            {
                rgb[i] = node;
                node = strpbrk(node," \n");
                if(node != NULL)
                {
                    *node++ = 0;
                }
                else
                {
                    is_valid = false;
                    break;
                }
            }

            if(is_valid)
            {
                set_rgb_from_arr(handle,rgb);
            }
        }
    }
    else if(strcasecmp(argv[1], "rgb") == 0)
    {
        set_rgb_from_arr(handle,(const char**)argv+2);
    }
    else
    {
        usage(argv[0]);
        exit(1);
    }

    usb_close(handle);
    return EXIT_SUCCESS;
}
