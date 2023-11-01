def transition(x,y):
    if x == 0:
        trans_x = "a"
    elif  x == 1:
        trans_x = "b"
    elif  x == 2:
        trans_x = "c"
    elif  x == 3:
        trans_x = "d"
    elif  x == 4:
        trans_x = "e"
    elif  x == 5:
        trans_x = "f"
    elif  x == 6:
        trans_x = "g"
    elif  x == 7:
        trans_x = "h"

    trans_y = str(8 - y)

    return "".join([trans_x, trans_y])

   
def run():
    print(transition(2, 2))

if __name__ == '__main__':
    run() 