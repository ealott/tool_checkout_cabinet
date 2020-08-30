VALID_FACILITY_CODES = [ '123']
VALID_CARDS = [ '12345' ]

# def wiegand_2_card(number):
#     """wiegand_2_card(number)
#         number : integer
#         returns list of strings [str, ...]
#     """
#     min_ = 11       # facility 1 and user 1 with no padding
#     max_ = 25565535 # facility 255 and user 65535 with no padding
#     number = str(number)
#     candidates = []
#     res = []
#     for i in candidates:
#         facility_code_bin = format(i[0], '08b') # padding here may be useless
#         user_code_bin = format(i[1], '016b')    # padding here is necessary
#         res.append(str(int(f'{facility_code_bin}{user_code_bin}', 2)))
#     return res

# 7462364
# 01001010 1111001110011100
#wiegand library returns separate facility code and card number in decimal format.  To get the number printed on the card, we need to convert both to binary, concatenate, then convert back to decimal.
def wiegand26_decode(facility_code, card):
    facility_code_bin="{0:b}".format(facility_code)                                                                                                                            
    card_bin="{0:b}".format(card)                                                                                                                                                                                                                                                  
    return int(facility_code_bin+card_bin,2)  

from wiegand import Wiegand
WIEGAND_ZERO = 12  # Pin number here
WIEGAND_ONE = 13   # Pin number here



def on_card(card_number, facility_code, cards_read):
    print('facility code: ' + str(facility_code) + '|' + 'card read:' + str(card_number) + '|' + str(cards_read) )
    print("Decoded: " + str(wiegand26_decode(facility_code, card_number)))
reader=Wiegand(WIEGAND_ZERO, WIEGAND_ONE, on_card)