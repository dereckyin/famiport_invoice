

class Toolkit:
    
    def __init__(self):
        super().__init__()

    @staticmethod
    def divide_into_chuncks(data_list, chunck_size):
        chuncks = []

        for x in range(0, len(data_list), chunck_size):
            chuncks.append(data_list[x:x+chunck_size])

        return chuncks