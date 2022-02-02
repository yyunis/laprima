from cmu_112_graphics import *
from dataclasses import make_dataclass
import random
import math

#game reference: https://www.coolmathgames.com/0-coffee-shop 
#tutorials from https://www.cs.cmu.edu/~112/notes/notes-animations-part4.html#ioMethods 
#with the help of helena yang, my TP mentor!! thank you helena :-)

################# APP STARTED #######################################

def appStarted(app):
    app.margin = min(app.width, app.height)/15
    app.startScreen = True
    app.instructions1 = False
    app.instructions2 = False
    app.beginGame = False
    app.inventoryPage = False
    app.startDay = False
    app.endDay = False
    app.day = Day(1, 0, 0, 0, 0, 30.00, 0, 0, 0, 0)
    app.coffeeSliderX = (3.3/12)*app.width
    app.coffeeSliderY = (6*app.margin)
    app.milkSliderX = (6.1/12)*app.width
    app.milkSliderY = 6*app.margin
    app.sugarSliderX = (9.1/12)*app.width
    app.sugarSliderY = 6*app.margin
    app.SliderR = app.margin/13
    app.cartImage = app.loadImage('coffeecart.jpeg')
    app.cartImage = app.scaleImage(app.cartImage, 1/3)
    app.customerImage = app.loadImage('customer.png')
    app.customerImage = app.scaleImage(app.customerImage, 1/4)
    app.customerImage = app.customerImage.transpose(Image.FLIP_LEFT_RIGHT)
    app.timestart = 0
    #change later to automatically generate
    firstCustomer = Customer(0, getPreference(app.day.coffeeRecipe, app.day.milkRecipe, app.day.sugarRecipe, app.day.weather, app.day.sellPrice), stopAtStand(app))
    app.customersL = [firstCustomer]
    app.totalCustomers = 0
    app.pauseDay = False
    app.totalRating = 0

############## DAY CLASS ####################
#rounding learned from https://stackoverflow.com/questions/20457038/how-to-round-to-2-decimals-with-python
class Day(object):
    def __init__(self, dayNumber, cups, coffee, milk, sugar, money, tickets, coffeeRecipe, milkRecipe, sugRecipe):
        self.Num = dayNumber
        self.cups = cups
        self.coffee = coffee
        self.milk = milk
        self.sugar = sugar
        self.money = money
        self.itemsBought = []
        self.weather = random.randint(30, 85)
        self.tickets = tickets
        self.cupPrice = 0.14
        self.coffeePrice = 0.40
        self.milkPrice = 0.10
        self.sugarPrice = 0.25
        self.cupRecipe = 1
        self.coffeeRecipe = coffeeRecipe
        self.milkRecipe = milkRecipe
        self.sugarRecipe = sugRecipe
        self.sellPrice = 1.00
        self.clock = 7
        self.timePassed = 0
        self.time = 0
        self.soldOut = False
        (self.maxCoffee, self.maxMilk, self.maxSugar, self.maxPrice) = self.hillClimbing()
        self.reveal1 = False
        self.reveal2 = False
        self.reveal3 = False
        self.revealAll = False

    def getDayNumber(self):
        return self.Num
    
######### input + adjusting actual numbers ############
    def addCups(self, num):
        self.cups += num
        self.money -= (num*self.cupPrice)
        self.money = round(self.money, 2)

    def addCoffee(self, num):
        self.coffee += num
        self.money -= (num*self.coffeePrice)
        self.money = round(self.money, 2)
        
    def addMilk(self, num):
        self.milk += num
        self.money -= (num*self.milkPrice)
        self.money = round(self.money, 2)

    def addSugar(self, num):
        self.sugar += num
        self.money -= (num*self.sugarPrice)
        self.money = round(self.money, 2)

    def getTickets(self):
        return self.tickets

    def findServings(self):
        if self.coffeeRecipe == 0 or self.milkRecipe == 0 or self.sugarRecipe == 0:
            return 0
        else:
            cupServings = self.cups/self.cupRecipe
            coffeeServings = self.coffee/self.coffeeRecipe
            milkServings = self.milk/self.milkRecipe
            sugarServings = self.sugar/self.sugarRecipe
            return int(min(cupServings, coffeeServings, milkServings, sugarServings))

    def findLimitation(self):
        if self.cups == 0 or self.coffee == 0 or self.milk == 0 or self.sugar == 0:
            return "N/A"
        else:
            if self.cupRecipe == 0:
                cupServings = 100000000
            else:
                cupServings = self.cups/self.cupRecipe
            if self.coffeeRecipe == 0:
                coffeeServings = 100000000
            else:
                coffeeServings = self.coffee/self.coffeeRecipe
            if self.milkRecipe == 0:
                milkServings = 100000000
            else:
                milkServings = self.milk/self.milkRecipe
            if self.sugarRecipe == 0:
                sugarServings = 100000000
            else:
                sugarServings = self.sugar/self.sugarRecipe
            if int(cupServings) == int(min(cupServings, coffeeServings, milkServings, sugarServings)):
                return "Cups"
            elif int(coffeeServings) == int(min(cupServings, coffeeServings, milkServings, sugarServings)):
                return "Coffee"   
            elif int(milkServings) == int(min(cupServings, coffeeServings, milkServings, sugarServings)):    
                return "Milk"
            elif int(sugarServings) == int(min(cupServings, coffeeServings, milkServings, sugarServings)):    
                return "Sugar"

    def timerFired(self, app):
        self.time += 40
        if self.time % 4000 == 0:
            self.clock += 1
            self.timePassed += 1
            if app.pauseDay == True:
                self.clock -= 1
        
    def getDayTime(self):
        if self.clock == 12:
            self.clock = 12
        else:
            self.clock = self.clock%12
        return self.clock

    ################ HILL CLIMBING ###################
    #https://www.geeksforgeeks.org/introduction-hill-climbing-artificial-intelligence/ 
    #https://www.section.io/engineering-education/understanding-hill-climbing-in-ai/

    def hillClimbing(self):
        coff = self.coffeeRecipe
        milk = self.milkRecipe
        sug = self.sugarRecipe
        weather = self.weather
        price = self.sellPrice
        dCoff = prefDerCoffee(coff)
        dMilk = prefDerMilk(milk)
        dSug = prefDerSugar(sug)
        dPrice = prefDerPrice(weather, price)
        bound = 0.000001
        step = 0.001
        while abs(dCoff) > bound and abs(dMilk) > bound and abs(dSug) > bound and abs(dPrice) > bound:
            coff = coff + dCoff*step
            milk = milk + dMilk*step
            sug = sug + dSug*step
            price = price + dPrice*step
            weather = weather
            dCoff = prefDerCoffee(coff)
            dMilk = prefDerMilk(milk)
            dSug = prefDerSugar(sug)
            dPrice = prefDerPrice(weather, price)
        coff = round(coff, 2)
        if coff > 4.0:
            coff = 4
        if coff < 0.01:
            coff = 0.01
        milk = round(milk, 2)
        if milk > 2.0:
            milk = 2
        if milk < 0.01:
            milk = 0.01
        sug = round(sug, 2)
        if sug > 4.0:
            sug = 4
        if sug < 0.01:
            sug = 0.01
        price = round(price, 2)
        if price > 10.0:
            price = 10
        if price < 0.01:
            price = 0.01
        return (coff, milk, sug, price)

################ customer graphics ###################
# format from https://www.cs.cmu.edu/~112/notes/notes-oop-part2.html#oopExample OOP animation
# 'customer' image: http://clipart-library.com/clipart/1529862.htm 

class Customer(object):
    def __init__(self, x, preference, stop):
        self.x = x
        #change later to be based off preference method
        self.preference = preference
        self.pauseTime = 0
        self.stopAtStand = stop
        self.rating = self.preference/120 #change to preference/max

    def redraw(self, app, canvas):
        canvas.create_image(self.x, 405, image=ImageTk.PhotoImage(app.customerImage))

    def timerFired(self, app):
        self.x += 10
        if app.pauseDay == True:
            self.x -= 10
        if self.stopAtStand:
            if self.x == (2/3)*app.width:
                if self.pauseTime < 2000:
                    self.x -= 10
                    self.pauseTime += 150

####################### TIMER FIRED  ########################

def timerFired(app):
    app.timestart += app.timerDelay
    app.day.time += app.timerDelay
    if app.startDay == True:
        for dog in app.customersL:
            dog.timerFired(app)
            app.day.timerFired(app)
            if dog.x == (2/3)*app.width and dog.stopAtStand == True:
                sellCoffee(app)
                collectTickets(app)
        #creating new dogs at diff times
        if app.pauseDay == True:
            pass
        elif app.timestart % 4000 == 0:
            newDog = Customer(0, getPreference(app.day.coffeeRecipe, app.day.milkRecipe, app.day.sugarRecipe, app.day.weather, app.day.sellPrice), stopAtStand(app))
            app.customersL.append(newDog)
        elif app.timestart % 5000 == 0:
            newDog1 = Customer(0, getPreference(app.day.coffeeRecipe, app.day.milkRecipe, app.day.sugarRecipe, app.day.weather, app.day.sellPrice), stopAtStand(app))
            app.customersL.append(newDog1)
        elif app.timestart % 7000 == 0:
            newDog2 = Customer(0, getPreference(app.day.coffeeRecipe, app.day.milkRecipe, app.day.sugarRecipe, app.day.weather, app.day.sellPrice), stopAtStand(app))
            app.customersL.append(newDog2)
        if (app.day.cups < app.day.cupRecipe or 
            app.day.coffee < app.day.coffeeRecipe or 
            app.day.milk < app.day.milkRecipe or 
            app.day.sugar < app.day.sugarRecipe):
            app.pauseDay = True
            app.day.soldOut = True
        if app.day.timePassed >= 12:
            app.pauseDay = True

################## MOUSE PRESSED ######################################

#return true or false value
def pressButtonCheck(app, event, x1, x2, y1, y2, m1, m2):
    if (app.x in range(int(x1*app.width), int(x2*app.width)) and 
        app.y in range(int(y1*app.height + m1*app.margin),
                    int(y2*app.height + m2*app.margin))):
        return True
    return False

def distance(x0, y0, x1, y1):
    return math.sqrt((x1-x0)**2 + (y1-y0)**2)

def mousePressed(app, event):
    app.x = event.x
    app.y = event.y
    #if press play, start game
    if app.startScreen == True:
        if pressButtonCheck(app, event, 1/4, 3/4, 1/2, 1/2, -1, 1):
            app.beginGame = True
        #if press instruction, show instruction screen
        if pressButtonCheck(app, event, 1/4, 3/4, 2/3, 2/3, -1, 1):
            app.startScreen = False
            app.instructions1 = True
    if app.instructions1 == True:
        if pressButtonCheck(app, event, 1/7, 3/7, 1, 1, -2.5, -1):
            app.instructions1 = False
            app.startScreen = True
        if pressButtonCheck(app, event, 4/7, 6/7, 1, 1, -2.5, -1):
            app.instructions2 = True
            app.instructions1 = False
    if app.instructions2 == True:
        if pressButtonCheck(app, event, 2.5/7, 4.5/7, 1, 1, -2.5, -1):
            app.instructions2 = False
            app.instructions1 = True
    if app.beginGame == True:
        if pressButtonCheck(app, event, 2.5/7, 4.5/7, 3/5, 3/5, -1, 1):
            app.beginGame = False
            app.inventoryPage = True
    if app.inventoryPage == True:
        #press cups button
        if pressButtonCheck(app, event, 1.2/12, 3.5/12, 1/4, 1/4, -.25, .25):
            cupNum = getCupInput(app)
        #press coffee button
        if pressButtonCheck(app, event, 3.75/12, 6/12, 1/4, 1/4, -.25, .25):
            coffeeNum = getCoffeeInput(app)
        #press milk button
        if pressButtonCheck(app, event, 6.25/12, 8.5/12, 1/4, 1/4, -.25, .25):
            milkNum = getMilkInput(app)
        #press sugar button
        if pressButtonCheck(app, event, 8.75/12, 11/12, 1/4, 1/4, -.25, .25):
            sugarNum = getSugarInput(app)
        #undo button
        if pressButtonCheck(app, event, 9.5/12, 10.5/12, 1/4.8, 1/4.8, -.2, .2):
            undoPurchase(app)
        #press the coffee circle
        if distance(app.x, app.y, app.coffeeSliderX, app.coffeeSliderY) < app.SliderR:
            mouseDragged(app, event)
        #press milk circle
        if distance(app.x, app.y, app.milkSliderX, app.milkSliderY) < app.SliderR:
            mouseDragged(app, event)
        #press sugar circle
        if distance(app.x, app.y, app.sugarSliderX, app.sugarSliderY) < app.SliderR:
            mouseDragged(app, event)
        #press adjust price
        if pressButtonCheck(app, event, 3.8/15, 5.25/15, 8/15, 8/15, -.2, .2):
            getPriceInput(app)
        #press start day
        if pressButtonCheck(app, event, 1.5/15, 4.75/15, 13.5/15, 13.5/15, -.25, .25):
            app.inventoryPage = False
            app.startDay = True
        if pressButtonCheck(app, event, 3.25/15, 5.75/15, 10.15/15, 10.15/15, -.3, .3) and app.day.tickets >= 2:
            app.day.tickets -= 2
            app.day.tickets = round(app.day.tickets, 2)
            app.day.reveal1 = True
        if pressButtonCheck(app, event, 3.25/15, 5.75/15, 11.15/15, 11.15/15, -.3, .3) and app.day.tickets >= 4:
            app.day.tickets -= 4
            app.day.tickets = round(app.day.tickets, 2)
            app.day.reveal2 = True
        if pressButtonCheck(app, event, 3.25/15, 5.75/15, 12.15/15, 12.15/15, -.3, .3) and app.day.tickets >= 5:
            app.day.tickets -= 5
            app.day.tickets = round(app.day.tickets, 2)
            app.day.reveal3 = True
        if pressButtonCheck(app, event, 10.25/15, 13.25/15, 10.3/15, 10.3/15, -.3, .3) and app.day.tickets >= 10:
            app.day.tickets -= 10
            app.day.tickets = round(app.day.tickets, 2)
            app.day.revealAll = True
    if app.startDay == True:
        if pressButtonCheck(app, event, 10.75/15, 14/15, 13.75/15, 13.75/15, -.25, .25):
            app.startDay = False
            app.pauseDay = False
            app.endDay = True
    if app.endDay == True:
        if pressButtonCheck(app, event, 1/4, 3/4, 3/4, 3/4, -1, 1):
            if app.day.getDayNumber() < 5:
                currDayNum = app.day.getDayNumber()
                currCups = app.day.cups
                currCoffee = app.day.coffee
                currMilk = app.day.milk
                currSugar = app.day.sugar
                currMoney = app.day.money
                currTickets = app.day.tickets
                currCoffRec = app.day.coffeeRecipe
                currMilkRec = app.day.milkRecipe
                currSugarRec = app.day.sugarRecipe
                #maybe keep same recipe??
                app.day = Day(currDayNum + 1, currCups, currCoffee, currMilk, currSugar, currMoney, currTickets, currCoffRec, currMilkRec, currSugarRec)
                app.endDay = False
                app.beginGame = True

####################### MOUSE DRAGGED #######################

def mouseDragged(app, event):
    if app.inventoryPage == True:
        #coffee
        if (event.x <= ((4.8/12)*app.width) and event.x >= ((3.3/12)*app.width)
            and event.y in range(int(app.coffeeSliderY-app.SliderR), int(app.coffeeSliderY+app.SliderR))):
            app.coffeeSliderX = event.x
            mouseReleased(app, event)
        #milk
        if (event.x <= ((7.6/12)*app.width) and event.x >= ((6.1/12)*app.width)
            and event.y in range(int(app.milkSliderY-app.SliderR), int(app.milkSliderY+app.SliderR))):
            app.milkSliderX = event.x
            mouseReleased(app, event)
        #sugar
        if (event.x <= ((10.6/12)*app.width) and event.x >= ((9.1/12)*app.width)
            and event.y in range(int(app.sugarSliderY-app.SliderR), int(app.sugarSliderY+app.SliderR))):
            app.sugarSliderX = event.x
            mouseReleased(app, event)
 
def mouseReleased(app, event):
    if app.inventoryPage == True:
        #coffee
        if event.x <= ((4.8/12)*app.width + app.SliderR) and event.x >= ((3.3/12)*app.width - app.SliderR):
            diff = (app.coffeeSliderX - (3.3/12)*app.width)
            lengthOfLine = (4.8/12)*app.width - (3.3/12)*app.width
            ratio = diff/lengthOfLine
            app.day.coffeeRecipe = round(ratio*4.01, 1)
        #milk
        if event.x <= ((7.6/12)*app.width + app.SliderR) and event.x >= ((6.1/12)*app.width - app.SliderR):
            diff = (app.milkSliderX - (6.1/12)*app.width)
            lengthOfLine = (7.6/12)*app.width - (6.1/12)*app.width
            ratio = diff/lengthOfLine
            app.day.milkRecipe = round(ratio*2, 1)
        #sugar
        if event.x <= ((10.6/12)*app.width + app.SliderR) and event.x >= ((9.1/12)*app.width - app.SliderR):
            diff = (app.sugarSliderX - (9.1/12)*app.width)
            lengthOfLine = (10.6/12)*app.width - (9.1/12)*app.width
            ratio = diff/lengthOfLine
            app.day.sugarRecipe = round(ratio*4, 1)

################ get user input ####################
def getCupInput(app):
    cupNum = app.getUserInput("Enter the number of cups you'd like to purchase:")
    if cupNum == None:
        app.showMessage("You canceled your purchase!")
        cupNum = 0
    cupNum = int(cupNum)
    totalCost = round(cupNum*app.day.cupPrice, 2)
    if (totalCost) > app.day.money:
        app.showMessage("Not enough money!")
        cupNum = 0
    if cupNum != 0 and totalCost <= app.day.money:
        app.day.addCups(int(cupNum))
        app.day.itemsBought.append(("cups", cupNum, totalCost))

def getCoffeeInput(app):
    coffeeNum = app.getUserInput("Enter the number of tspns of coffee you'd like to purchase:")
    if coffeeNum == None:
        app.showMessage("You canceled your purchase!")
        coffeeNum = 0
    coffeeNum = int(coffeeNum)
    totalCost = round(coffeeNum*app.day.coffeePrice, 2)
    if (totalCost) > app.day.money:
        app.showMessage("Not enough money!")
        coffeeNum = 0
    if coffeeNum != 0 and totalCost <= app.day.money:
        app.day.addCoffee(int(coffeeNum))
        app.day.itemsBought.append(("coffee", coffeeNum, totalCost))

def getMilkInput(app):
    milkNum = app.getUserInput("Enter the number of cups of milk you'd like to purchase:")
    if milkNum == None:
        app.showMessage("You canceled your purchase!")
        milkNum = 0
    milkNum = int(milkNum)
    totalCost = round(milkNum*app.day.milkPrice, 2)
    if (totalCost) > app.day.money:
        app.showMessage("Not enough money!")
        milkNum = 0
    if milkNum != 0 and totalCost <= app.day.money:
        app.day.addMilk(int(milkNum))
        app.day.itemsBought.append(("milk", milkNum, totalCost))

def getSugarInput(app):
    sugarNum = app.getUserInput("Enter the number of tspns of sugar you'd like to purchase:")
    if sugarNum == None:
        app.showMessage("You canceled your purchase!")
        sugarNum = 0
    sugarNum = int(sugarNum)
    totalCost = round(sugarNum*app.day.sugarPrice, 2)
    if (totalCost) > app.day.money:
        app.showMessage("Not enough money!")
        sugarNum = 0
    if sugarNum != 0 and totalCost <= app.day.money:
        app.day.addSugar(int(sugarNum))
        app.day.itemsBought.append(("sugar", sugarNum, totalCost))

def getPriceInput(app):
    price = app.getUserInput("Enter the selling price of your coffee from $0.01 to $10.00")
    if price == None or price == "":
        price = 1.00
    app.day.sellPrice = float(price)

################## UNDO PURCHASE FUNCTION ###############
def undoPurchase(app):
    if app.day.itemsBought != []:
        undo = app.day.itemsBought.pop()
        if undo[0] == "cups":
            app.day.cups -= undo[1]
            app.day.cups = round(app.day.cups, 2)
        elif undo[0] == "coffee":
            app.day.coffee -= undo[1]
            app.day.coffee = round(app.day.coffee, 2)
        elif undo[0] == "milk":
            app.day.milk -= undo[1]
            app.day.milk = round(app.day.milk, 2)
        elif undo[0] == "sugar":
            app.day.sugar -= undo[1]
            app.day.sugar = round(app.day.sugar, 2)
        app.day.money += round(undo[2], 2)
        app.day.money = round(app.day.money, 2)
    else: app.showMessage("No purchase to undo!")

############### SELL COFFEE FUNCTION ################

def sellCoffee(app):
    if app.pauseDay == False:
        app.totalCustomers += 1
        app.day.cups -= round(app.day.cupRecipe, 2)
        app.day.cups = round(app.day.cups, 2)
        app.day.coffee -= round(app.day.coffeeRecipe, 2)
        app.day.coffee = round(app.day.coffee, 2)
        app.day.milk -= round(app.day.milkRecipe, 2)
        app.day.milk = round(app.day.milk, 2)
        app.day.sugar -= round(app.day.sugarRecipe, 2)
        app.day.sugar = round(app.day.sugar, 2)
        app.day.money += round(app.day.sellPrice, 2)
        app.day.money = round(app.day.money, 2)

############### GET RATING + TICKET FROM CUSTOMER ############
def collectTickets(app):
    residual = math.sqrt((app.day.coffeeRecipe - app.day.maxCoffee)**2 + (app.day.milkRecipe - app.day.maxMilk)**2 + (app.day.sugarRecipe - app.day.maxSugar)**2 + (app.day.sellPrice - app.day.maxPrice)**2)
    rating = 1/residual
    app.totalRating += rating
    app.day.tickets += rating*(0.5)
    app.day.tickets = round(app.day.tickets, 2)

############## PREFERENCE FUNCTION ####################
#preference is set daily (based on recipe)
#each dog has the preference method calculated
def getPreference(c, m, s, w, p):
    return (-0.5*(c**4) + 2*(c**3) + 3*(c**2) + c 
        - 6*(m**2) + 18*m -
        (1/6)*(s**5) + (2/3)*(s**4) + (1/3)*s**3 - 4*(s**2) + 11*s + 10
        + (100/w)*(((-1/50)*(-((p-4)**2)))+20))

# ############ preference function derivatives ############

def prefDerCoffee(c):
    derivative = ((-2)*(c**3) + 6*(c**2) + 6*c + 1)
    return derivative

def prefDerMilk(m):
    derivative = ((-12)*m + 18)
    return derivative

def prefDerSugar(s):
    derivative = ((-5/6)*(s**4) + (8/3)*(s**3) + s**2 - 8*s + 11)
    return derivative

def prefDerPrice(w, p):
    derivative = (1/w)*(1/25)*(p-4)
    return derivative

###################### HINT STRING ####################
def hintString(number):
    if number < 0:
        second = "decrease"
    elif number > 0:
        second = "increase"
    else:
        second = ""
    if abs(number) > 6:
        first = "Strongly "
    elif 0.01 < abs(number) <= 6:
        first = "Mildly "
    else:
        first = "Don't change"
    return first+second


##################### STOP AT STAND ###################
#for stop at stand:
#choice instruction from https://www.geeksforgeeks.org/how-to-get-weighted-random-choice-in-python/ 

def stopAtStand(app):
        preference = getPreference(app.day.coffeeRecipe, app.day.milkRecipe, app.day.sugarRecipe, app.day.weather, app.day.sellPrice)
        choice = [True, False]
        maxPreference = getPreference(app.day.maxCoffee, app.day.maxMilk, app.day.maxSugar, app.day.weather, app.day.maxPrice)
        if preference > (0.8)*(maxPreference):  #find max PREFFFF and use
            chosen = random.choices(choice, weights=(75, 25))
            return chosen[0]
        else:
            chosen = random.choices(choice, weights=(10, 90))
            return chosen[0]

################### GAME VERY BEGINNING PAGE #######################
def drawStart(app, canvas):
    if app.startScreen == True:
        canvas.create_rectangle(0, 0, app.width, app.height, fill="beige")
        #bar on top + bottom
        canvas.create_rectangle(0, 0, app.width, 1.5*app.margin, fill="brown")
        canvas.create_rectangle(0, app.height-1.5*app.margin, app.width, 
            app.height, fill="brown")
        #title of game
        canvas.create_text(app.width/2, app.height/3, text="La Prima", 
            fill="darkBlue", font="Times 28 bold italic")
        #play button rectangle
        canvas.create_rectangle(app.width/4, app.height/2 - app.margin, 
            3*app.width/4, app.height/2 + app.margin, fill="tan", 
            outline="brown", width=2)
        #play button name
        canvas.create_text(app.width/2, app.height/2, text="Play", 
            font="Times 16 bold")
        #instructions
        canvas.create_rectangle(app.width/4, 2*app.height/3 - app.margin,
            3*app.width/4, 2*app.height/3 + app.margin, fill="tan",
            outline="brown", width=2)
        canvas.create_text(app.width/2, 2*app.height/3, text="Instructions", 
            font="Times 16 bold")

############# INSTRUCTIONS ####################
def generalText(app, canvas, depth, script):
    canvas.create_text(app.width/2, depth*app.margin, text=script, font="Times 14")

def drawButtons(app, canvas, x1, x2, y1, m1, m2, script):
    canvas.create_rectangle(x1*app.width, y1*app.height + m1*app.margin,
            x2*app.width, y1*app.height + m2*app.margin, fill="tan", width=2)
    canvas.create_text(((x1+x2)/2)*app.width, y1*app.height + ((m1+m2)/2)*app.margin,
            text=script, font="Times 14")

def drawSlider(app, canvas, x1, x2, range1, range2, variableX, variableY, variableZ):
    canvas.create_line((x1)*app.width, 6*app.margin, (x2)*app.width, 6*app.margin)
    canvas.create_text((x1)*app.width, 6.3*app.margin, text=range1, font="Times 10")
    canvas.create_text((x2)*app.width, 6.3*app.margin, text=range2, font="Times 10")
        #small lines
    canvas.create_line((x1)*app.width, 6*app.margin - app.margin/11, (x1)*app.width, 6*app.margin+app.margin/11)
    canvas.create_line((x2)*app.width, 6*app.margin - app.margin/11, (x2)*app.width, 6*app.margin+app.margin/11)
        #button on slider
    canvas.create_oval(variableX - app.SliderR, variableY - app.SliderR,
        variableX + app.SliderR, variableY + app.SliderR, fill="darkGray")
    canvas.create_text((x2 + 0.3/12)*app.width, 6*app.margin, text=f"{variableZ}", font="Times 10")


#emojis from https://emojicombos.com/cute-kaomoji
#instructions similar to https://www.coolmathgames.com/0-coffee-shop 
def drawInstructions1(app, canvas):
    if app.instructions1 == True:
        canvas.create_rectangle(0, 0, app.width, app.height, fill="beige")
        #welcome + rules
        canvas.create_text(app.width/2, 2*app.margin, text="Welcome to La Prima!",
            font="Times 28 bold")
        generalText(app, canvas, 3.5, "Your goal is to make the most profit possible")
        generalText(app, canvas, 4, "over the next 5 days!")
        generalText(app, canvas, 5, "Every day, you will purchase your ingredients")
        generalText(app, canvas, 6, "and change the recipe of your coffee. You may")
        generalText(app, canvas, 7, "also adjust the price of your coffee")
        generalText(app, canvas, 8.5, "Coffee has 4 ingredients that you can purchase:")
        canvas.create_text(app.width/2, 9*app.margin,
            text="• Cups\n• Coffee\n• Milk\n• Sugar", anchor="n",
            font="Times 14")
        #next page button
        drawButtons(app, canvas, 4/7, 6/7, 1, -2.5, -1, "Next ₍ᵔ•ᴗ•ᵔ₎")
        #start page button
        drawButtons(app, canvas, 1/7, 3/7, 1, -2.5, -1, "Start Page")

#emojis from https://emojicombos.com/cute-kaomoji
def drawInstructions2(app, canvas):
    if app.instructions2 == True:
        canvas.create_rectangle(0, 0, app.width, app.height, fill="beige")
        generalText(app, canvas, 2, "The cost per unit of coffee depends on your recipe!")
        generalText(app, canvas, 3, "Your recipe also determines your customers' ratings.")
        generalText(app, canvas, 3.75, "Generally, customers like more of each ingredient (๑•͈ᴗ•͈)")
        generalText(app, canvas, 4.5, "Adjusting the sell price of your coffee is important~")
        generalText(app, canvas, 5.5, "Don't make the coffee too pricy!")
        generalText(app, canvas, 6.25, "But try to make the most money possible.")
        generalText(app, canvas, 7, "Customers will pay more on colder days ( ੭ ･ᴗ･ )੭")
        generalText(app, canvas, 8.5, "You may adjust your recipe and inventory")
        generalText(app, canvas, 9.25, "at the beginning of each day and you can")
        generalText(app, canvas, 10, "adjust the price of your coffee during the day!")
        generalText(app, canvas, 11, "You're ready to start! Good luck! (ʃƪ˘⌣˘)")
        #previous button
        drawButtons(app, canvas, 2.5/7, 4.5/7, 1, -2.5, -1, "Back (˙༥˙(")

############# START PAGE (before inventory) #####################
def drawGameStart(app, canvas):
    if app.beginGame == True:
        canvas.create_rectangle(0, 0, app.width, app.height, fill="beige")
        canvas.create_rectangle(app.margin, app.margin, app.width-app.margin, app.height-app.margin,
            fill='lightGray', width=3)
        canvas.create_text(app.width/2, 1/3*app.height,
            text=f"Welcome to Day {app.day.getDayNumber()}!")
        canvas.create_text(app.width/2, 2.25*app.height/5,
            text="Click the inventory button to purchase and restock:")
        drawButtons(app, canvas, 2.5/7, 4.5/7, 3/5, -1, 1, "Inventory")


#arrows from: https://unicode.org/charts/nameslist/n_2190.html 
############## INVENTORY PAGE ###################
def drawInventoryPage(app, canvas):
    if app.inventoryPage == True:
        canvas.create_rectangle(0, 0, app.width, app.height, fill="beige")
        canvas.create_rectangle(app.margin, app.margin, app.width-app.margin, app.height-app.margin,
                fill='lightGray', width=3)
        #TOP of inventory
        canvas.create_text((1.25/5)*app.width, 2*app.margin, text=f"Day {app.day.getDayNumber()}",
            font="Times 16 bold")
        canvas.create_text((2.5/5)*app.width, 2*app.margin, text=f"Weather: {app.day.weather}º",
            font="Times 16 bold")
        canvas.create_text((3.75/5)*app.width, 2*app.margin, text=f"Money: ${app.day.money}",
            font="Times 16 bold")
        #STOCK
        canvas.create_text(1.5*app.margin, 3*app.margin, text="Inventory (Click icon to purchase):",
            font="Times 16 bold", fill="darkBlue", anchor="w")
        drawButtons(app, canvas, 1.2/12, 3.5/12, 1/4, -.25, .25, f"Cups (${app.day.cupPrice}/unit)")
        canvas.create_text((2.35/12)*app.width, app.height/4 + app.margin/2, text=f"↪Quantity: {app.day.cups}")
        drawButtons(app, canvas, 3.75/12, 6/12, 1/4, -.25, .25, f"Coffee (${app.day.coffeePrice}/tsp)")
        canvas.create_text((4.875/12)*app.width, app.height/4 + app.margin/2, text=f"↪Quantity: {app.day.coffee}")
        drawButtons(app, canvas, 6.25/12, 8.5/12, 1/4, -.25, .25, f"Milk (${app.day.milkPrice}/cup)")
        canvas.create_text((7.375/12)*app.width, app.height/4 + app.margin/2, text=f"↪Quantity: {app.day.milk}")
        drawButtons(app, canvas, 8.75/12, 11/12, 1/4, -.25, .25, f"Sugar (${app.day.sugarPrice}/tsp)")
        canvas.create_text((9.875/12)*app.width, app.height/4 + app.margin/2, text=f"↪Quantity: {app.day.sugar}")
        #undo button
        drawButtons(app, canvas, 9.5/12, 10.5/12, 1/4.8, -.2, .2, "Undo")
        #### CREATING RECIPE ADJUSTMENTS #########
        canvas.create_text(1.5*app.margin, 5.25*app.margin, text="Recipe (Slide to adjust):",
            font="Times 16 bold", fill="darkBlue", anchor="w")
        canvas.create_text((1.75/12)*app.width, 6*app.margin, text=f"Cups: {app.day.cupRecipe}", font="Times 11 bold")
        #coffee slider
        canvas.create_text((2.5/12)*app.width, 6*app.margin, text=f"Coffee:", anchor="w", font="Times 11 bold")
        drawSlider(app, canvas, 3.3/12, 4.8/12, 0, 4, app.coffeeSliderX, app.coffeeSliderY, app.day.coffeeRecipe)
        #milk slider
        canvas.create_text((5.4/12)*app.width, 6*app.margin, text="Milk:", anchor="w", font="Times 11 bold")
        drawSlider(app, canvas, 6.1/12, 7.6/12, 0, 2, app.milkSliderX, app.milkSliderY, app.day.milkRecipe)
        #sugar slider
        canvas.create_text((8.3/12)*app.width, 6*app.margin, text="Sugar:", anchor="w", font="Times 11 bold")
        drawSlider(app, canvas, 9.1/12, 10.6/12, 0, 4, app.sugarSliderX, app.sugarSliderY, app.day.sugarRecipe)
        ############# SERVINGS #########################
        canvas.create_text(1.5*app.margin, 7*app.margin, text=f"Servings: {app.day.findServings()}", anchor="w", font="Times 14 bold")
        ############# LIMITED BY ########################
        canvas.create_text(4*app.margin, 7*app.margin, text=f"Limited by: {app.day.findLimitation()}", anchor="w", font="Times 14 bold")
        ############## selling price of coffee ############
        canvas.create_text(1.6*app.margin, 8*app.margin, text=f"Price: ${app.day.sellPrice}", anchor="w")
        drawButtons(app, canvas, 3.8/15, 5.25/15, 8/15, -.2, .2, "Adjust")
        ############# START DAY BUTTON #################
        drawButtons(app, canvas, 1.5/15, 4.75/15, 13.5/15, -.25, .25, "Start Day!")
        ############ TICKETS ###########################
        canvas.create_text(11*app.margin, 9*app.margin, text=f"Tickets: {app.day.tickets}", anchor="w")
        ############# HINTS #########################
        canvas.create_text(1.5*app.margin, 9*app.margin, text="Purchase hints with tickets!! ૮ ˶ᵔ ᵕ ᵔ˶ ა", anchor="w", fill="darkBlue", font="Times 16 bold")
        drawButtons(app, canvas, 3.25/15, 5.75/15, 10.15/15, -.3, .3, "Hint #1")
        canvas.create_text(2.3*app.margin, 10.1/15*app.height, text="2 tickets", font="Times 13")
        drawButtons(app, canvas, 3.25/15, 5.75/15, 11.15/15, -.3, .3, "Hint #2")
        canvas.create_text(2.3*app.margin, 11.1/15*app.height, text="4 tickets", font="Times 13")
        drawButtons(app, canvas, 3.25/15, 5.75/15, 12.15/15, -.3, .3, "Hint #3")
        canvas.create_text(2.3*app.margin, 12.1/15*app.height, text="5 tickets", font="Times 13")
        if app.day.reveal1 == True:
            partialCoffee = prefDerCoffee(app.day.coffeeRecipe)
            hint1 = hintString(partialCoffee)
            canvas.create_text(6/15*app.width, 10.15/15*app.height, text=f"Coffee: {hint1}", anchor="w")
        if app.day.reveal2 == True:
            partialMilk = prefDerMilk(app.day.milkRecipe)
            hint2 = hintString(partialMilk)
            canvas.create_text(6/15*app.width, 11.15/15*app.height, text=f"Milk: {hint2}", anchor="w")
        if app.day.reveal3 == True:
            partialSugar = prefDerSugar(app.day.sugarRecipe)
            hint3 = hintString(partialSugar)
            canvas.create_text(6/15*app.width, 12.15/15*app.height, text=f"Sugar: {hint3}", anchor="w")
        canvas.create_text(11.75/15*app.width, 9.7/15*app.height, text="10 tickets", font="Times 13")
        drawButtons(app, canvas, 10.25/15, 13.25/15, 10.3/15, -.3, .3, "Reveal Solution")
        if app.day.revealAll == True:
            canvas.create_text(10.5/15*app.width, 11/15*app.height, text=f"Coffee: {app.day.maxCoffee}", anchor="w")
            canvas.create_text(10.5/15*app.width, 11.45/15*app.height, text=f"Milk: {app.day.maxMilk}", anchor="w")
            canvas.create_text(10.5/15*app.width, 11.9/15*app.height, text=f"Sugar: {app.day.maxSugar}", anchor="w")

############ START DAY PAGE ###########
def drawStartDay(app, canvas):
    if app.startDay == True:
        canvas.create_rectangle(0, 0, app.width, app.height, fill="white")
        canvas.create_text((1/7)*app.width, 1.5*app.margin, text=f"Day {app.day.getDayNumber()}",
            font="Times 16 bold")
        canvas.create_text((2.5/7)*app.width, 1.5*app.margin, text=f"Weather: {app.day.weather}º",
            font="Times 16 bold")
        canvas.create_text((4/7)*app.width, 1.5*app.margin, text=f"Time: {app.day.getDayTime()}",
            font="Times 16 bold")
        canvas.create_text((5.5/7)*app.width, 1.5*app.margin, text=f"Money: ${app.day.money}",
            font="Times 16 bold")
        drawCart(app, canvas)
        drawDayInventory(app, canvas)
        canvas.create_rectangle(0, app.height-3.6*app.margin, app.width, app.height, fill="green")
        for dog in app.customersL:
            dog.redraw(app, canvas)

#cart inspo from https://www.istockphoto.com/illustrations/coffee-cart 
def drawCart(app, canvas):
    canvas.create_image((2/3)*app.width, (1/2)*app.height, image=ImageTk.PhotoImage(app.cartImage))

def drawDayInventory(app, canvas):
    canvas.create_rectangle(app.margin, 2.5*app.margin, (1/2.4)*app.width, app.height/2, fill="brown")
    canvas.create_rectangle(app.margin+8, 2.5*app.margin+8, (1/2.4)*app.width-8, app.height/2-8, fill="tan", outline="white")
    canvas.create_text(app.margin+15, 2.5*app.margin+20, text="Inventory", anchor="w", font="Times 16 bold")
    canvas.create_text(app.margin+15, 3.5*app.margin, text=f"Cups remaining: {app.day.cups}", anchor="w")
    canvas.create_text(app.margin+15, 4.25*app.margin, text=f"Coffee remaining: {app.day.coffee}", anchor="w")
    canvas.create_text(app.margin+15, 5*app.margin, text=f"Milk remaining: {app.day.milk}", anchor="w")
    canvas.create_text(app.margin+15, 5.75*app.margin, text=f"Sugar remaining: {app.day.sugar}", anchor="w")
    if app.pauseDay == True:
        if app.day.soldOut == True:
            canvas.create_text(3.65*app.margin, 6.6*app.margin, text=f"SOLD OUT", font="Times 20 bold", fill="red")
        else:
            canvas.create_text(3.65*app.margin, 6.6*app.margin, text=f"DAY ENDED", font="Times 20 bold", fill="red")

def drawPauseDay(app, canvas):
    if app.pauseDay == True:
        drawButtons(app, canvas, 10.75/15, 14/15, 13.75/15, -.25, .25, "End Day >")

################# end of day recap ###################
def drawEndDay(app, canvas):
    if app.endDay == True:
        canvas.create_rectangle(0, 0, app.width, app.height, fill="beige")
        canvas.create_rectangle(app.margin, app.margin, app.width-app.margin, app.height-app.margin,
            fill='lightGray', width=3)
        canvas.create_text(app.width/2, 3*app.margin, text=f"End of Day {app.day.getDayNumber()}")
        if app.day.soldOut == True:
            canvas.create_text(app.width/2, 4*app.margin, text=f"Day {app.day.getDayNumber()} has ended due to one or more ingredients being sold out!")
        else:
            canvas.create_text(app.width/2, 4*app.margin, text=f"Day {app.day.getDayNumber()} has ended!")
        canvas.create_text(app.width/2, 5*app.margin, text=f"Total customers served: {app.totalCustomers}")
        canvas.create_text(app.width/2, 6*app.margin, text=f"Average rating: {round(app.totalRating/app.totalCustomers, 2)} Scottie Dogs")
        canvas.create_text(app.width/2, 7*app.margin, text=f"Current total: ${app.day.money}")
        #use ratings that change
        tickets = round(app.day.tickets, 2)
        canvas.create_text(app.width/2, 8*app.margin, text=f"Current tickets: {tickets}")
        if int(app.day.getDayNumber()) < 5:
            nextDay = int(app.day.getDayNumber()) + 1
            drawButtons(app, canvas, 1/4, 3/4, 3/4, -1, 1, f"Start Day {nextDay}")
        else:
            canvas.create_text(app.width/2, 3/4*app.height, text=f"Congrats! You're done with the game! ଘ(੭*ˊᵕˋ)੭* ੈ♡‧₊˚")

############# redraw all ######################
def redrawAll(app, canvas):
    drawStart(app, canvas)
    drawInstructions1(app, canvas)
    drawInstructions2(app, canvas)
    drawGameStart(app, canvas)
    drawInventoryPage(app, canvas)
    drawStartDay(app, canvas)
    drawPauseDay(app, canvas)
    drawEndDay(app, canvas)

#############################################

runApp(width=600, height=600)












