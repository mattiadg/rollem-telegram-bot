#!/bin/python
import sys
import time
import telepot
import random
import re

ladder = {
    8  : 'Legendary',
    7  : 'Epic',
    6  : 'Fantastic',
    5  : 'Superb',
    4  : 'Great',
    3  : 'Good',
    2  : 'Fair',
    1  : 'Average',
    0  : 'Mediocre',
    -1 : 'Poor',
    -2 : 'Terrible'
}
      ##########################################
######## Used for any commands that roll dice ########
########  CMDs: /roll, /r, /rf                ########
      ##########################################
class Dice:
    def __init__(self):
        self.fate_options = { 
            -1 : '[\u2012]', 
            0  : '[  ]', 
            1  : '[+]' 
        }

    ####################
    ## Set Attributes ##
    ####################
    def set_attrbs(self, content_list):
        self.content_list = content_list
        self.label = ''
        self.modifier = ''
        
        # Find label and modifier if they exist
        labelat = 2
        if self.content_list[0] == '/rf':
            if len(self.content_list) >= 2:
                try:
                    if isinstance(eval(self.content_list[1]), int):
                        self.modifier = self.content_list[1]
                        labelat = 2
                except NameError:
                    labelat = 1

            if len(self.modifier):
                self.equation = '4dF' + '+' + str(self.modifier)
            else:
                self.equation = '4dF'
                
        else:
            self.equation = content_list[1]

        if len(self.content_list) >= (labelat + 1):
            msg_begin, keyword, msg_end = curnt_input.content.partition(self.content_list[labelat])
            self.label = ' ' + keyword + msg_end

        print('New request: ' + self.equation)
            
        # Break apart equation by operators
        self.equation_list = re.findall(r'([(]?)(\w+)([+*/()-]*)', self.equation)

    ##################
    ##  Get ladder  ##
    ##################
    def get_ladder(self):
        # Set if final result is positive or negative
        if self.result['total'] > -1:
            sign = '+'
        else:
            sign = ''

        # Set ladder value for final result
        if self.result['total'] < -2:
            ladder_result = 'Beyond Terrible'
        elif self.result['total'] > 8:
            ladder_result = 'Beyond Legendary'
        else:
            ladder_result = ladder[self.result['total']]

        self.result['total'] = sign + str(self.result['total']) + ' ' + ladder_result

    ################
    ##  Roll dice ##
    ################
    def roll(self):

        self.result = {
            'visual': [],
            'equation': [],
            'total': ''
        }

        # Break apart each chunk of the equation by numbers and letters 
        # if dice notation
        space = ''
        isfate = False
        use_ladder = False

        try: 
            for pair in self.equation_list:
                for i in pair:
                    dice = re.search(r'(\d*)d([0-9fF]+)', str(i))
                    if dice:
                        self.result['visual'].append(space + '(')
                        self.result['equation'].append('(')
                        space = ' '
                        # Set number of dice to roll
                        if len(dice.group(1)):
                            loop_num = eval(str(dice.group(1))) 
                        else:
                            loop_num = 1

                        fate_dice = ''
                        current_die_results = ''
                        plus = ''
                        
                        # Roll dice
                        while loop_num > 0:
                            if dice.group(2) == 'f' or dice.group(2) == 'F':
                                isfate = True
                                current_fate_die = random.choice(list(self.fate_options.keys()))
                                current_die_results += plus + str(current_fate_die)
                                fate_dice += self.fate_options[current_fate_die] + ' '
                            else: 
                                current_die_results += plus + str(random.randint(1,eval(dice.group(2))))
                            if len(plus) is 0: # Adds all results to result unless it is the first one
                                plus = ' + '
                            loop_num -= 1
                        
                        if isfate:
                            isfate = False
                            use_ladder = True
                            self.result['visual'].append(' ' + fate_dice)
                        else:
                            self.result['visual'].append(current_die_results)
                        self.result['equation'].append(current_die_results)
                        self.result['visual'].append(')')
                        self.result['equation'].append(')')
                    else:
                        self.result['visual'].append(' ')
                        self.result['visual'].append(i)
                        self.result['equation'].append(i)

            self.result['total'] = eval(str(''.join(self.result['equation'])))

            print(''.join(self.result['equation']) + ' = ' + str(self.result['total']))

            if use_ladder:
                self.get_ladder()

            response = (curnt_input.user + ' rolled<b>' + self.label + '</b>:\r\n'        
                + ''.join(self.result['visual']) + ' =\r\n<b>' + str(self.result['total']) + '</b>')

        except Exception:
            response = (curnt_input.user + ': <b>Invalid equation!</b>\r\n' +
                'Please use <a href="https://en.wikipedia.org/wiki/Dice_notation">dice notation</a>.\r\n' +
                'For example: <code>3d6</code>, or <code>1d20+5</code>, or <code>d12</code>')

        return response


class Input:
    def __init__(self):
        self.isset = False
        self.is_command = False
        self.commands = [
            '/r',
            '/roll',
            '/rf'
        ]

    ####################
    ## Set Attributes ##
    ####################
    def set_attrbs(self, msg):
        self.isset = True
        self.msg = msg
        self.content_type, self.chat_type, self.chat_id = telepot.glance(msg)
        if 'username' in msg['from'].keys():
            self.user = msg['from']['username']
        else:
            self.user = msg['from']['first_name'] 

        #Get command
        self.is_command = False
        if self.content_type == 'text':
            self.content = msg['text']
            self.content_list = self.content.split()
            if self.content_list[0] in self.commands:
                self.is_command = True

        print(self.content_type, self.chat_type, self.chat_id)

        if self.is_command:
            self.process()

    ##################### Will be used later to determine where to send the content.
    ## Process Message ## For example, if an NPC generator is included, the content 
    ##################### would be sent to a different class than one to roll dice.
    def process(self):

        curnt_dice.set_attrbs(self.content_list)
        response = curnt_dice.roll()

        # Respond to user with results
        bot.sendMessage(self.chat_id, response, 'HTML', True)

curnt_input = Input()
curnt_dice = Dice()

def handle(msg):
    curnt_input.set_attrbs(msg)

TOKEN = sys.argv[1] # get token from command line

bot = telepot.Bot(TOKEN)
bot.message_loop(handle)
print ('Listening...')

# Keep the program running
while 1:
    time.sleep(10)
