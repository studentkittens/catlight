/* Name: catlight.c
 * Author: C. Pahl, based on code by Christian Starkjohann
 * Creation Date: 2012-4-20
 * License: GNU GPL v3
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>
#include <stdint.h>
#include <error.h>
#include <errno.h>
#include <unistd.h>
#include <termios.h>
#include <fcntl.h>
#include <sys/ioctl.h>
#include <glib.h>
#include <usb.h>

#define USB 0
#define MAX_BUF_LEN 256

/* Taken from original firmware/request.h */
#define CUSTOM_RQ_SET_RED    3
#define CUSTOM_RQ_SET_GREEN  4
#define CUSTOM_RQ_SET_BLUE   5

/* Taken from original firmware/usbconfig.h */
#define USB_CFG_VENDOR_ID   0xc0, 0x16
#define USB_CFG_DEVICE_ID   0xdf, 0x05
#define USB_CFG_VENDOR_NAME 'd', 'a', 'v', 'e', '.', 'h'
#define USB_CFG_DEVICE_NAME 'L', 'E', 'D', 'C', 't', 'l', 'H', 'I', 'D'

/**
 * @brief Print usage
 *
 * @param name Name of the program (argv[0])
 */
static void usage(char *name)
{
    fprintf(stderr, "usage:\n");
    fprintf(stderr, "  %s on  ....... turn on LED (white)\n", name);
    fprintf(stderr, "  %s off ....... turn off LED\n", name);
    fprintf(stderr, "  %s cat ....... read rgb tuples from stdin\n", name);
    fprintf(stderr, "  %s rgb  r g b  Set LED color to r,g,b\n", name);
    fprintf(stderr, "  %s hex #FFFFFF Set LED color from hexstring\n", name);
    exit(1);
}

//////////////////////////////////

#if USB
/**
 * @brief Match a string against a shell style pattern (hello?world*)
 *
 * @param text the text to check
 * @param pattern the pattern, NULL is a valid pattern, always returning true
 *
 * @return true if both match, false if not or if text is NULL
 */
static bool shell_style_match(const char * text, const char * pattern)
{
    if(pattern == NULL)
        return true;

    return text ? g_pattern_match_simple(text,pattern) : 0;
}

///////////////////////////////////

/**
 * @brief Gets a string by ID from the device and tests it agains a shell pattern
 *
 * @param handle the opened device
 * @param ID the ID of the string to query
 * @param buf a buf to write the result into
 * @param buflen the max. length of buf
 * @param query_pattern the shell pattern to test
 *
 * @return false on no match, true on match
 */
static bool query_and_match(usb_dev_handle * handle, int ID, char * buf, size_t buflen, const char * query_pattern)
{
    memset(buf,0,buflen);
    size_t len  = usb_get_string_simple(handle, ID, buf, buflen);
    if(len > 0)
        return shell_style_match(buf,query_pattern);
    else
        return false;
}

///////////////////////////////////

/**
 * @brief Open the catlight device
 *
 * @param device  the opened devive, passed as reference
 * @param vendorID the ID of the vendor
 * @param vendorNamePattern pattern to check vendor against
 * @param productID the ID of the product
 * @param productNamePattern pattern to check product against
 * @param serialNamePattern pattern to check serial against
 *
 * @return 0 on success, other values on failure
 */
static int open_device(usb_dev_handle **device, int vendorID, char *vendorNamePattern, int productID, char *productNamePattern, char *serialNamePattern)
{
    struct usb_bus * bus = NULL;
    struct usb_device * dev = NULL;
    usb_dev_handle * handle = NULL;
    int errorCode = -1;
    char vendor[MAX_BUF_LEN], product[MAX_BUF_LEN], serial[MAX_BUF_LEN];

    if(device == NULL)
        return -1;

    usb_find_busses();
    usb_find_devices();

    for(bus = usb_get_busses(); bus && handle == NULL; bus = bus->next)
    {
        for(dev = bus->devices; dev && handle == NULL; dev = dev->next)
        {
            if((vendorID  == 0 || dev->descriptor.idVendor == vendorID)
            && (productID == 0 || dev->descriptor.idProduct == productID))
            {
                handle = usb_open(dev);
                if(handle != NULL)
                {
                    if(query_and_match(handle,dev->descriptor.iManufacturer,vendor,sizeof(vendor),vendorNamePattern)   &&
                       query_and_match(handle,dev->descriptor.iProduct,product,    sizeof(product),productNamePattern) &&
                       query_and_match(handle,dev->descriptor.iSerialNumber,serial,sizeof(serial),serialNamePattern))
                    {
                        *device = handle;
                        errorCode = 0;
                        break;
                    }

                    usb_close(handle);
                    handle = NULL;
                }
            }
        }
    }

    return errorCode;
}

/**
 * @brief Set the actual color (0-255 x 3) for an actual device
 *
 * @param handle a opened handle, no error checking is done!
 * @param r red color part
 * @param g green color part
 * @param b blue color part
 */
static void set_rgb(usb_dev_handle * handle, int r, int g, int b)
{
    const int timeout = 5000;
    int flags = USB_TYPE_VENDOR | USB_RECIP_DEVICE | USB_ENDPOINT_OUT;
    usb_control_msg(handle, flags, CUSTOM_RQ_SET_RED,   r, 0, NULL, 0, timeout);
    usb_control_msg(handle, flags, CUSTOM_RQ_SET_GREEN, g, 0, NULL, 0, timeout);
    usb_control_msg(handle, flags, CUSTOM_RQ_SET_BLUE,  b, 0, NULL, 0, timeout);
}

#else

//////////////////////////////////

/**
 * @brief Open the catlight device for arduino
 *
 * @param fd the opened devive, passed as reference
 * @param portname name of the serial port
 * @param baudrate communication speed
 *
 * @return 0 on success, other values on failure
 */
static int open_device(int *fd, char *portname, int baudrate)
{
    struct termios tty;
    memset(&tty, 0, sizeof(tty));

    *fd = open(portname, O_RDWR | O_NOCTTY);

    if (*fd < 0)
        return -1;
    if (tcgetattr(*fd, &tty) != 0)
        return -1;

    cfsetospeed (&tty, baudrate);
    cfsetispeed (&tty, baudrate);

    tty.c_cflag |= (CLOCAL | CREAD);
    tty.c_cflag &= ~CSIZE;
    tty.c_cflag |= CS8;
    tty.c_cflag &= ~PARENB;
    tty.c_cflag &= ~CSTOPB;
    tty.c_lflag |= ICANON;
    tty.c_lflag &= ~( ISIG | ECHO | ECHOE);
    tty.c_cflag &= ~HUPCL;

    if (tcsetattr(*fd, TCSANOW, &tty) != 0)
        return -1;

    return 0;
}

//////////////////////////////////

static void set_rgb(int fd, int r, int g, int b)
{
    unsigned char buf[5];
    buf[0] = 0x02;
    buf[1] = (unsigned char)r;
    buf[2] = (unsigned char)g;
    buf[3] = (unsigned char)b;
    buf[4] = 0x03;
    printf("%02X %02X %02X %02X %02X\n", buf[0], buf[1], buf[2], buf[3], buf[4]);
    write(fd, buf, 5);
}
#endif

//////////////////////////////////

/**
 * @brief Tries to convert a string containing a number to a number in the range [0-255]
 *
 * @param arg a valid string
 *
 * @return the resulting number, or 0 on failure
 */
static int string_to_col(const char * arg)
{
    return CLAMP(strtol(arg,NULL,10),0,255);
}

//////////////////////////////////

/**
 * @brief Takes an array of 3 strings and set the color accordingly
 *
 * @param handle the open device
 * @param arr a string array
 */
#if USB
static void set_rgb_from_arr(usb_dev_handle * handle, const char ** arr)
#else
static void set_rgb_from_arr(int handle, const char ** arr)
#endif
{
    int r,g,b;
    r = string_to_col(arr[0]);
    g = string_to_col(arr[1]);
    b = string_to_col(arr[2]);

    set_rgb(handle,r,g,b);
}

//////////////////////////////////

/**
 * @brief Converts a string of the form ABCDEF to a rgb tupel
 *
 * @param str a hex string (without #, with containing spaces or newline at the end)
 * @param r out for red
 * @param g out for green
 * @param b out for blue
 */
static void hexstring_to_rgb(const char * str, unsigned * r, unsigned * g, unsigned * b)
{
    char * is_err = NULL;
    if(!(str && r && g && b))
        return;

    union {
        uint32_t val;
        unsigned char arr[sizeof(uint32_t)];
    } rgb_int = {.val=0};

    rgb_int.val = strtoul(str,&is_err,0x10);

    if(is_err == NULL || *is_err == '\n' || *is_err == 0)
    {
// BB|GG|RR|00
#if G_BYTE_ORDER == G_LITTLE_ENDIAN
        *r = rgb_int.arr[2];
        *g = rgb_int.arr[1];
        *b = rgb_int.arr[0];
// 00|BB|GG|RR
#elif G_BYTE_ORDER == G_BIG_ENDIAN
        *r = rgb_int.arr[3];
        *g = rgb_int.arr[2];
        *b = rgb_int.arr[1];
#else
        // Not supported, PDP endian is brainfuck.
#endif
    }
}

//////////////////////////////////

/**
 * @brief The main..
 *
 * Opens the device and depending on the mode
 * input is read from the cmd or from stdin
 *
 * @param argc
 * @param argv
 *
 * @return 0 on success, a pretty much random value on failure
 */
int main(int argc, char **argv)
{
#if USB
    usb_dev_handle * handle = NULL;
    const unsigned char rawVid[2] = {USB_CFG_VENDOR_ID};
    const unsigned char rawPid[2] = {USB_CFG_DEVICE_ID};
    char vendor[] = {USB_CFG_VENDOR_NAME, 0};
    char product[] = {USB_CFG_DEVICE_NAME, 0};
    int vid, pid;

    usb_init();
#else
    int handle;
#endif

    if(argc < 2)
        usage(argv[0]);

#if USB
    /* compute VID/PID from usbconfig.h so that there is a central source of information */
    vid = rawVid[1] * 256 + rawVid[0];
    pid = rawPid[1] * 256 + rawPid[0];

    if(open_device(&handle, vid, vendor, pid, product, NULL) != 0)
    {
        fprintf(stderr, "Could not find USB device \"%s\" with vid=0x%x pid=0x%x\n", product, vid, pid);
        exit(1);
    }
#else
    if (open_device(&handle, "/dev/ttyACM0", B115200) != 0)
        error(1, errno, "Could not open device");
#endif

    if(strcasecmp(argv[1], "cat") == 0)
    {
        const int size = 1024;
        char buf[size+1];
        const char * rgb[3] = {0,0,0};
        int i = 0;

        for(;;)
        {
            memset(buf,0,size);
            if(fgets(buf,size,stdin) == NULL)
            {
                puts("Got EOF, quitting");
                break;
            }

            if(buf[0] == '#')
            {
                unsigned r = 0, g = 0, b = 0;
                hexstring_to_rgb(&buf[1],&r,&g,&b);
                set_rgb(handle,r,g,b);
            }
            else
            {
                bool is_valid = true;
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
    }
    else if(strcasecmp(argv[1], "rgb") == 0 && argc > 4)
    {
        set_rgb_from_arr(handle,(const char**)&argv[2]);
    }
    else if(strcasecmp(argv[1], "hex") == 0)
    {
        unsigned r = 0, g = 0, b = 0;
        printf("%s\n",&argv[2][1]);
        hexstring_to_rgb(&argv[2][1],&r,&g,&b);
        set_rgb(handle,r,g,b);
    }
    else if(strcasecmp(argv[1], "on") == 0)
    {
        set_rgb(handle,255,255,255);
    }
    else if(strcasecmp(argv[1], "off") == 0)
    {
        set_rgb(handle,0,0,0);
    }
    else
    {
        usage(argv[0]);
    }

#if USB
    usb_close(handle);
#else
    close(handle);
#endif
    return EXIT_SUCCESS;
}
