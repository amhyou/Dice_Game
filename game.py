import sys, os, hashlib, hmac, random
from tabulate import tabulate
from itertools import product

class Dice:
    def __init__(self, faces: list):
        self.faces = list(map(int, faces))

class Dices:
    def __init__(self, args: list):
        self.dices = []
        self.validate_arguments(args)
        for arg in args:
            self.dices.append(Dice(arg.split(",")))
    

    def validate_arguments(self, args):
        if len(args) < 3:
            raise ValueError("You must provide at least 3 dice configurations.")
        for arg in args:
            if arg.count(",") != 5:
                raise ValueError(f"Invalid dice configuration: '{arg}'. Each dice must have exactly 6 values separated by commas.")
            try:
                faces = list(map(int, arg.split(",")))
            except ValueError:
                raise ValueError(f"Invalid dice configuration: '{arg}'. All values must be integers.")
            if len(faces) != 6:
                raise ValueError(f"Invalid dice configuration: '{arg}'. Each dice must have exactly 6 sides.")

    def dice_number(self) -> int:
        return len(self.dices)


class TableGeneration:
    def __init__(self, faces: list):
        self.dices = faces

    def display(self):

        header = ["User dice v"] + [",".join([str(i) for i in die]) for die in self.dices]
        rows = []

        instance = Probability()
        probabilities = instance.calculate_probabilities(self.dices)

        for i, die in enumerate(self.dices):
            row = [",".join([str(i) for i in die])]
            for j in range(len(self.dices)):
                row.append(probabilities[i][j])
            rows.append(row)
        print("Probability of the win for the user:")
        print(tabulate(rows, headers=header, tablefmt="grid"))

class Probability:
    def calculate_probabilities(self, dice):
        n = len(dice)
        probabilities = [[0.0 for _ in range(n)] for _ in range(n)]
        
        for i in range(n):
            for j in range(n):
                if i == j:
                    probabilities[i][j] = "-------"
                    continue
                
                die_a = dice[i]
                die_b = dice[j]
                
                total_outcomes = len(die_a) * len(die_b)
                win_a, win_b, tie = 0, 0, 0
                
                for face_a, face_b in product(die_a, die_b):
                    if face_a > face_b:
                        win_a += 1
                    elif face_a < face_b:
                        win_b += 1
                    else:
                        tie += 1
                
                probabilities[i][j] = round(win_a / total_outcomes, 4)
                probabilities[j][i] = round(win_b / total_outcomes, 4)
        
        return probabilities


class HashGeneration:
    def __init__(self):
        self.__key = os.urandom(32)

    def get_signature(self, msg: str):
        hmac_obj = hmac.new(self.__key, msg.encode('utf-8'), hashlib.sha3_256)
        hmac_digest = hmac_obj.hexdigest()
        return hmac_digest.upper()

    def get_secret_key(self):
        return self.__key.hex().upper()
    
class FairNumber:
    def __init__(self, upper_limit: int):
        self.hg = HashGeneration()
        self.number = random.choice(range(upper_limit))
        hashed_choice = self.hg.get_signature(str(self.number))
        print(f"I selected a random value in the range 0..{upper_limit-1}")
        print(f"(HMAC={hashed_choice}).")

class Game:

    def __init__(self):
        self.computer_turn: int = None
        self.choosen_dices: list[Dice] = [ None, None ]
        try:
            self.dices = Dices(sys.argv[1:])
        except ValueError as e:
            print(f"Error: {e}")
            exit()

        self.turn_selection()
        self.dice_selection()
        self.throw_definition()
    

    def turn_selection(self):
        print("Let's determine who makes the first move.")
        turn = FairNumber(2)
        print("Try to guess my selection.")
        predicted_turn = self.choice_selection([0, 1])
        self.computer_turn = predicted_turn == turn.number
        print(f"My selection: {turn.number} (KEY={turn.hg.get_secret_key()}).")


    def dice_selection(self):
        if self.computer_turn:
            print("You make the first move")
            print("Choose your dice:")
            choice = self.choice_selection([ d.faces for d in self.dices.dices])
            user_dice = self.dices.dices[choice]
            print(f"You choose the {user_dice.faces} dice.")
            computer_dice_i = random.choice([ i for i in range(self.dices.dice_number()) if i!= choice])
            computer_dice = self.dices.dices[computer_dice_i]
            print(f"I choose the {computer_dice.faces} dice.")
        else:
            computer_dice_i = random.choice([ i for i in range(self.dices.dice_number())])
            computer_dice = self.dices.dices[computer_dice_i]
            print(f"I make the first move and choose the {computer_dice.faces} dice.")
            print("Choose your dice:")
            choice = self.choice_selection([ self.dices.dices[i].faces for i in range(self.dices.dice_number()) if i!= computer_dice_i])
            user_dice = self.dices.dices[choice] if choice < computer_dice_i else self.dices.dices[choice+1]
            print(f"You choose the {user_dice.faces} dice.")
        
        self.choosen_dices[self.computer_turn] = computer_dice
        self.choosen_dices[1-self.computer_turn] = user_dice


    def throw_definition(self):
        print("It's time for my throw.")
        computer_number = FairNumber(6)
        print("Add your number modulo 6.")
        user_number = self.choice_selection([0,1,2,3,4,5])
        print(f"My number is {computer_number.number} (KEY={computer_number.hg.get_secret_key()}).")
        computer_throw = ( computer_number.number + user_number ) % 6
        print(f"The result is {computer_number.number} + {user_number} = {computer_throw} (mod 6).")
        computer_value = self.choosen_dices[self.computer_turn].faces[computer_throw]
        print(f"My throw is {computer_value}.")

        print("It's time for your throw.")
        computer_number2 = FairNumber(6)
        print("Add your number modulo 6.")
        user_number2 = self.choice_selection([0,1,2,3,4,5])
        print(f"My number is {computer_number2.number} (KEY={computer_number2.hg.get_secret_key()}).")
        user_throw = ( computer_number2.number + user_number2 ) % 6
        print(f"The result is {computer_number2.number} + {user_number2} = {user_throw} (mod 6).")
        user_value = self.choosen_dices[1-self.computer_turn].faces[user_throw]
        print(f"Your throw is {user_value}.")

        if user_value < computer_value:
            print(f"I win ({user_value} < {computer_value})!")
        elif user_value > computer_value:
            print(f"You win ({user_value} < {computer_value})!")
        else:
            print(f"Draw ({user_value} = {computer_value})!")


    def choice_selection(self, base: list) -> int:
        for i in range(len(base)):
            print(f"{i} - {base[i]}")
        print("X - exit")
        print("? - help")
        choice = input("Your selection: ")
        if choice in "012345":
            return int(choice)
        elif choice in "xX":
            print("The game is exited")
            exit()
        elif choice in "?":
            table = TableGeneration([d.faces for d in self.dices.dices])
            table.display()
            self.choice_selection(base)
        else:
            print("Your choice is not correct! try again:")
            self.choice_selection(base)
            

if __name__ == "__main__":
    Game()
