## Samsung Connect admin panel
# from urllib.request import urlopen
# from tkinter import *
import tkinter as tk
# from tkinter import filedialog
import es
# from tkinter import ttk

LARGE_FONT = ("Verdana", 12)

def main():
    app = SamsungConnect()
    app.title("Samsung Connect")
    app.mainloop()


class SamsungConnect(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)

        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        self.EditData = {}
        self.frames = {}

        for F in (StartPage, AddEntryPage, EditPage, EditEntryPage, DeleteEntryPage):
            frame = F(container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(StartPage)

    def send_info(self, data, parent, controller):
        EditPage.populate(data, parent, controller)

    def show_frame(self, cont):
        # if EditPage == cont:
        #     EditPage.load_data()
        frame = self.frames[cont]
        frame.tkraise()


class StartPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text="Admin Console", font=LARGE_FONT)
        label.pack(pady=10, padx=10)

        button = tk.Button(self, text="Add New Entry",
                           command=lambda: controller.show_frame(AddEntryPage))
        button.pack()
        button2 = tk.Button(self, text="Edit Entries",
                            command=lambda: controller.show_frame(EditEntryPage))
        button2.pack()
        button3 = tk.Button(self, text="Delete Entries",
                            command=lambda: controller.show_frame(DeleteEntryPage))
        button3.pack()


class AddEntryPage(tk.Frame):

    def __init__(self, parent, controller):

        tk.Frame.__init__(self, parent)
        info = get_info(self)

        labels = info[1]
        num_entries = info[0]
        max_pages = int(num_entries / 20)+1

        # number of rows to show
        self.num_rows = 20

        # entry data from form
        self.entry_data = []

        # holds the pages that contain an array of buttons
        self.pages = []

        # array to hold bounds
        self.lower_bounds = []
        self.upper_bounds = []

        for index in range(0, max_pages):
            self.lower_bounds.append(index*self.num_rows)
            self.pages.append(labels[index*self.num_rows:(index+1)*self.num_rows])
            self.upper_bounds.append((index+1)*self.num_rows)
            if index == max_pages:
                self.pages.append(labels[index+1*self.num_rows:num_entries])
                self.upper_bounds.append(num_entries)
        self.index = 0
        self.show_content(parent, controller)

    def show_content(self, parent, controller):

        # top buttons
        tk.Label(self, text="Add New Entries", font="Helvetica 16 bold") \
            .grid(row=0, sticky=tk.N, padx=4, pady=4)
        tk.Button(self, text="Back to Main Menu",
                  command=lambda: self.back_home(parent, controller)) \
            .grid(row=1, sticky=tk.W, pady=4)

        # place content onto a grid
        content = self.pages[self.index]
        for i in range(0, len(content)):
            data = content[i]
            data[0].grid(row=i+2, sticky=tk.W, padx=4)
            if data[1][:] == "child" or data[1][:] == "normal":
                tk.Entry(self, textvariable=data).grid(row=i+2, column=1, sticky=tk.E, pady=4)

        # pagination control & logic #

        # back button
        if self.index != 0:
            tk.Button(self, text="Back",
                      command=lambda: self.prev_page(parent, controller))\
                    .grid(row=self.num_rows + 3, sticky=tk.W)
        # save button
        if self.index == len(self.pages)-1:
            tk.Button(self, text="Save",
                      command=lambda: self.save())\
                    .grid(row=self.num_rows + 3, column=2, sticky=tk.E)
        # next button
        else:
            tk.Button(self, text="Next",
                command=lambda: self.next_page(parent, controller))\
                .grid(row=self.num_rows + 3, column=2, sticky=tk.E)

    def back_home(self, parent, controller):
        # AddEntryPage.__init__(self, parent, controller)
        controller.show_frame(StartPage)

    def next_page(self, parent, controller):
        self.store_content()
        self.destroy_content()
        self.index += 1
        self.show_content(parent, controller)

    def prev_page(self, parent, controller):
        self.store_content()
        self.destroy_content()
        self.index -= 1
        self.show_content(parent, controller)

    def store_content(self):
        temp = []
        for i in self.grid_slaves(column=1):
            data = i.get()
            # set default value
            if data == "":
                data = "false"
            temp.append(data)
        temp.reverse()
        self.entry_data[self.lower_bounds[self.index]:self.upper_bounds[self.index]] = temp

    def destroy_content(self):
        for i in self.grid_slaves():
            i.grid_remove()

    def save(self):
        self.store_content()
        id = ""
        fields = es.get_mappings()
        fields_length = len(fields)
        count = 0

        json = "{ \n"

        for index in range(0, fields_length):
            if isinstance(fields[index], dict):

                for key in fields[index]:
                    # single label no entry
                    json += "\"" + key + "\":" + "{"

                    for i in range(0, len(fields[index][key])):
                        json += "\"" + fields[index][key][i] + "\":\"" + self.entry_data[count]
                        count += 1
                        if i != len(fields[index][key])-1:
                            json += "\","
                        else:
                            json += "\""
                    json += "},\n"

            else:
                if fields[index] == "provider":
                    id = self.entry_data[count]

                json += "\"" + fields[index] + "\":\"" + self.entry_data[count]
                count += 1

                if index != fields_length-1:
                    json += "\",\n"
                else:
                    json += "\"\n"

        json += "}"
        es.add_entry(json, id)

    def destroy_page(self):
        for i in self.grid_slaves():
            i.destroy()


class EditPage(tk.Frame):

    def __init__(self, parent, controller):

        tk.Frame.__init__(self, parent)
        info = get_info(self)

        labels = info[1]
        num_entries = info[0]
        max_pages = int(num_entries / 20)+1

        # number of rows to show
        self.num_rows = 20

        # entry data from form
        self.entry_data = []

        # holds the pages that contain an array of buttons
        self.pages = []

        # array to hold bounds
        self.lower_bounds = []
        self.upper_bounds = []

        for index in range(0, max_pages):
            self.lower_bounds.append(index*self.num_rows)
            self.pages.append(labels[index*self.num_rows:(index+1)*self.num_rows])
            self.upper_bounds.append((index+1)*self.num_rows)
            if index == max_pages:
                self.pages.append(labels[index+1*self.num_rows:num_entries])
                self.upper_bounds.append(num_entries)
        self.index = 0
        # self.show_content(parent, controller)

    def populate(self, data, parent, controller):
        info = data['hits']['hits'][0]['_source']
        self.show_content(info, parent, controller)
        print(info)

    def show_content(self, info, parent, controller):

        # top buttons
        tk.Label(self, text="Edit Entries", font="Helvetica 16 bold") \
            .grid(row=0, sticky=tk.N, padx=4, pady=4)
        tk.Button(self, text="Back to Edit Menu",
                  command=lambda: self.back_home(parent, controller)) \
            .grid(row=1, sticky=tk.W, pady=4)

        # place content onto a grid
        content = self.pages[self.index]
        for i in range(0, len(content)):
            data = content[i]
            data[0].grid(row=i+2, sticky=tk.W, padx=4)
            if data[1][:] == "child" or data[1][:] == "normal":
                tk.Entry(self, textvariable=data, text="yes").grid(row=i+2, column=1, sticky=tk.E, pady=4)

        # pagination control & logic #

        # back button
        if self.index != 0:
            tk.Button(self, text="Back",
                      command=lambda: self.prev_page(parent, controller))\
                    .grid(row=self.num_rows + 3, sticky=tk.W)
        # save button
        if self.index == len(self.pages)-1:
            tk.Button(self, text="Save",
                      command=lambda: self.save())\
                    .grid(row=self.num_rows + 3, column=2, sticky=tk.E)
        # next button
        else:
            tk.Button(self, text="Next",
                command=lambda: self.next_page(parent, controller))\
                .grid(row=self.num_rows + 3, column=2, sticky=tk.E)

    def back_home(self, parent, controller):
        # AddEntryPage.__init__(self, parent, controller)
        controller.show_frame(EditEntryPage)

    def next_page(self, info, parent, controller):
        self.store_content()
        self.destroy_content()
        self.index += 1
        self.show_content(info, parent, controller)

    def prev_page(self, info, parent, controller):
        self.store_content()
        self.destroy_content()
        self.index -= 1
        self.show_content(info, parent, controller)

    def store_content(self):
        temp = []
        for i in self.grid_slaves(column=1):
            data = i.get()
            # set default value
            if data == "":
                data = "false"
            temp.append(data)
        temp.reverse()
        self.entry_data[self.lower_bounds[self.index]:self.upper_bounds[self.index]] = temp

    def destroy_content(self):
        for i in self.grid_slaves():
            i.grid_remove()

    def save(self):
        self.store_content()
        id = ""
        fields = es.get_mappings()
        fields_length = len(fields)
        count = 0

        json = "{ \n"

        for index in range(0, fields_length):
            if isinstance(fields[index], dict):

                for key in fields[index]:
                    # single label no entry
                    json += "\"" + key + "\":" + "{"

                    for i in range(0, len(fields[index][key])):
                        json += "\"" + fields[index][key][i] + "\":\"" + self.entry_data[count]
                        count += 1
                        if i != len(fields[index][key])-1:
                            json += "\","
                        else:
                            json += "\""
                    json += "},\n"

            else:
                if fields[index] == "provider":
                    id = self.entry_data[count]

                json += "\"" + fields[index] + "\":\"" + self.entry_data[count]
                count += 1

                if index != fields_length-1:
                    json += "\",\n"
                else:
                    json += "\"\n"

        json += "}"
        es.add_entry(json, id)

    def destroy_page(self):
        for i in self.grid_slaves():
            i.destroy()


class EditEntryPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        self.providers = es.get_all()
        num_entries = len(self.providers)
        names = []
        for i in self.providers:
            names.append(tk.Label(self, text=i['_source']['provider'], font="Helvetica 16 bold"))

        max_pages = int(num_entries / 20) + 1

        # number of rows to show
        self.num_rows = 20

        # entry data from form
        self.entry_data = []

        # holds the pages that contain an array of buttons
        self.pages = []

        # array to hold bounds
        self.lower_bounds = []
        self.upper_bounds = []

        for index in range(0, max_pages):
            self.lower_bounds.append(index * self.num_rows)
            self.pages.append(names[index * self.num_rows:(index + 1) * self.num_rows])
            self.upper_bounds.append((index + 1) * self.num_rows)
            if index == max_pages:
                self.pages.append(names[index + 1 * self.num_rows:num_entries])
                self.upper_bounds.append(num_entries)
        self.index = 0
        self.show_content(parent, controller)

    def show_content(self, parent, controller):
        # top buttons
        tk.Label(self, text="Edit Entries", font="Helvetica 16 bold")\
                .grid(row=0, sticky=tk.N, padx=4, pady=4)
        tk.Button(self, text="Back to Main Menu",
                  command=lambda: controller.show_frame(StartPage)) \
                .grid(row=1, sticky=tk.W, pady=4)

        # place content onto a grid
        count = 0
        content = self.pages[self.index]
        for i in range(0, len(content)):
            count += 1
            # print(i)
            data = content[i]
            data.grid(row=i + 2, sticky=tk.W, padx=4)
            tk.Button(self, text="Edit",
                      command=lambda j=i+0: self.edit(j, parent, controller))\
                .grid(row=i + 2, column=1, sticky=tk.E, pady=4)

        # pagination control & logic #

        # back button
        if self.index != 0:
            tk.Button(self, text="Back",
                      command=lambda: self.prev_page(parent, controller)) \
                .grid(row=self.num_rows + 3, sticky=tk.W)
        # save button
        if self.index == len(self.pages) - 1:
            tk.Button(self, text="Exit",
                      command=lambda: self.back_home(parent, controller)) \
                .grid(row=self.num_rows + 3, column=2, sticky=tk.E)
        # next button
        else:
            tk.Button(self, text="Next",
                      command=lambda: self.next_page(parent, controller)) \
                .grid(row=self.num_rows + 3, column=2, sticky=tk.E)

    def edit(self, index, parent, controller):
        response = es.search(self.providers[self.lower_bounds[self.index] + index]['_id'])
        controller.send_info(response, parent, controller)
        controller.show_frame(EditPage)

    def back_home(self, parent, controller):
        # AddEntryPage.__init__(self, parent, controller)
        controller.show_frame(StartPage)

    def next_page(self, parent, controller):
        self.destroy_content()
        self.index += 1
        self.show_content(parent, controller)

    def prev_page(self, parent, controller):
        self.destroy_content()
        self.index -= 1
        self.show_content(parent, controller)

    def destroy_content(self):
        for i in self.grid_slaves():
            i.grid_remove()

    def destroy_page(self):
        for i in self.grid_slaves():
            i.destroy()


class DeleteEntryPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        self.providers = es.get_all()
        num_entries = len(self.providers)
        names = []
        for i in self.providers:
            names.append(tk.Label(self, text=i['_source']['provider'], font="Helvetica 16 bold"))

        max_pages = int(num_entries / 20) + 1

        # number of rows to show
        self.num_rows = 20

        # entry data from form
        self.entry_data = []

        # holds the pages that contain an array of buttons
        self.pages = []

        # array to hold bounds
        self.lower_bounds = []
        self.upper_bounds = []

        # checkbox values
        self.checkbox_val = [0] * num_entries

        for index in range(0, max_pages):
            self.lower_bounds.append(index * self.num_rows)
            self.pages.append(names[index * self.num_rows:(index + 1) * self.num_rows])
            self.upper_bounds.append((index + 1) * self.num_rows)
            if index == max_pages:
                self.pages.append(names[index + 1 * self.num_rows:num_entries])
                self.upper_bounds.append(num_entries)
        self.index = 0
        self.show_content(parent, controller)

    def show_content(self, parent, controller):
        temp_checkbox = []
        # top buttons
        tk.Label(self, text="Delete Entry", font="Helvetica 16 bold") \
            .grid(row=0, sticky=tk.N, padx=4, pady=4)
        tk.Button(self, text="Back to Main Menu",
                  command=lambda: controller.show_frame(StartPage)) \
            .grid(row=1, sticky=tk.W, pady=4)

        # place content onto a grid
        content = self.pages[self.index]
        for i in range(0, len(content)):
            var = tk.IntVar()
            data = content[i]
            data.grid(row=i + 2, sticky=tk.W, padx=4)
            tk.Checkbutton(self, variable=var).grid(row=i + 2, column=1, sticky=tk.E, pady=4)
            temp_checkbox.append(var)

        # pagination control & logic #

        # back button
        if self.index != 0:
            tk.Button(self, text="Back",
                      command=lambda: self.prev_page(temp_checkbox, parent, controller)) \
                .grid(row=self.num_rows + 3, sticky=tk.W)
        # save button
        if self.index == len(self.pages) - 1:
            tk.Button(self, text="Save",
                      command=lambda: self.save(temp_checkbox)) \
                .grid(row=self.num_rows + 3, column=2, sticky=tk.E)
        # next button
        else:
            tk.Button(self, text="Next",
                      command=lambda: self.next_page(temp_checkbox, parent, controller)) \
                .grid(row=self.num_rows + 3, column=2, sticky=tk.E)

    def back_home(self, parent, controller):
        # AddEntryPage.__init__(self, parent, controller)
        controller.show_frame(StartPage)

    def next_page(self, temp_checkbox, parent, controller):
        self.store_content(temp_checkbox)
        self.destroy_content()
        self.index += 1
        self.show_content(parent, controller)

    def prev_page(self, temp_checkbox, parent, controller):
        self.store_content(temp_checkbox)
        self.destroy_content()
        self.index -= 1
        self.show_content(parent, controller)

    def store_content(self, temp_checkbox):
        for i in range(0, len(temp_checkbox)):
            self.checkbox_val[self.lower_bounds[self.index] + i] = temp_checkbox[i].get()

    def destroy_content(self):
        for i in self.grid_slaves():
            i.grid_remove()

    def save(self, temp_checkbox):
        self.store_content(temp_checkbox)
        for i in range(0, len(self.checkbox_val)):
            if self.checkbox_val[i] == 1:
                print(self.providers[i]['_id'])
                es.delete(self.providers[i]['_id'])

    def destroy_page(self):
        for i in self.grid_slaves():
            i.destroy()

def get_info(self):
    fields = es.get_mappings()
    fields_length = len(fields)

    field_names = []

    for index in range(0, fields_length):

        if isinstance(fields[index], dict):

            for key in fields[index]:
                # single label no entry
                field_names.append((tk.Label(self, text=key, font="Helvetica 16 bold"),
                                    "header"))

                for entry in fields[index][key]:
                    field_names.append((tk.Label(self, text="    " + entry),
                                        "child"))
        else:
            field_names.append((tk.Label(self, text=fields[index], font="Helvetica 16 bold"),
                               "normal"))
    return len(field_names), field_names


if __name__ == "__main__":
    main()

# If Windows, compile to Windows

# If Mac, compile to MacOS


