import led_connection
import threading
import time

class Effect(object):
    def __init__(self,options={}):
        """
        There are no default options,
        Certain effects may read from the dict as they like.

        What options a effect takes is documented there
        """
        self.set_options(options)

    def __del__(self):
        """
        Wait till effect has finished 
        and shutdown properly
        """
        if self.thread != None:
            try:
                if self.thread.is_alive():
                    self.thread.join()
            except RuntimeError as e:
                print(e)

    def start(self): 
        """
        Start the Effect
        """
        self.thread = None
        self.stop = False
        self.thread = threading.Thread(target=self.display())

    def kill(self):
        """
        Kill an effect explicitly before it stops itself
        (Some effects may run forever though)
        """
        if self.thread.is_alive():
            self.stop = True
            try:
                self.thread.join()
                self.thread = None
            except RuntimeError as e:
                print(e)
            self.stop = False

    def set_options(self,options):
        """
        Set options after instantiating,
        See __init__()
        """
        self.options = options

    def get_option(self,key,default):
        """
        Get a certain option, 
        this is meant for subclasses though 
        it may be useful for other users
        """
        try:
            return self.options[key]
        except KeyError:
            pass
        return default

    def display(self):
        """
        This method will be overwritten by a sublcass
        """
        raise NotImplementedError("You should overwrite display()") 




class Blink(Effect):
    """
    Simple blink effect that holds a certain 
    'color'(default:(255,255,255) for a certain time
    """
    def display(self):
        col = self.get_option('color',(255,255,255))
        led_connection.send(*col)
        time.sleep(self.get_option('duration',3))
        led_connection.off()


class SimpleFade(Effect):
    """
    A simple fade effects going linear from (0,0,0) to color 'color'(default: (255,255,255))
    and back to (0,0,0), the timeout can be specified via 'timeout'(default: 0.001)
    """
    def do_fade(self,flag=True,step=1):
        col = self.get_option('color',(255,255,255))
        timeout = self.get_option('timeout',0.001)

        off_r,off_g,off_b = 0,0,0
        for i in range(2):
            r,g,b = 0,0,0
            while r < col[0] or g < col[1] or b < col[2]: 
                if r < col[0]: r += step
                if g < col[1]: g += step
                if b < col[2]: b += step
                time.sleep(timeout)
                led_connection.send(off_r-r,off_g-g,off_b-b)
            off_r,off_g,off_b = col[0],col[1],col[2]
            
    def display(self):
        self.do_fade()

class Repeater(Effect):
    """
    Repeats the effects in 'effects'(default: []) 'times'(default: 5) time.
    time may be -1 for (almost) forever
    """
    def display(self):
        effect_list = self.get_option('effects',[])
        times  = self.get_option('times',5)

        if times < 0:
            times = 100000

        if len(effect_list) > 0:
            for i in range(times):
                for effect in effect_list:
                    effect.start()
                    effect.kill()


if __name__ == '__main__':
    effect_list = []
    for col in ((255,0,0),(255,255,0),(255,0,255),(255,255,255),(0,255,0),(0,0,255)):
        effect_list.append(SimpleFade({'timeout':0.001,'color':col}))
    
    Repeater({
        'effects' : effect_list,
        'times'   : -1
        }).start()

