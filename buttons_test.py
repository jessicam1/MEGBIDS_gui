#!/usr/bin/env python
import os
import PySimpleGUI as sg
import write_bids as wb
import subprocess

sg.theme('LightGrey3')   # Add a touch of color


# function for defacing mri file
def deface_mri(button_mri):
    fs_home = os.environ["FREESURFER_HOME"]
    face = os.path.join(fs_home, "average/face.gca")
    talairach = os.path.join(fs_home, "average/talairach_mixed_with_skull.gca")
    temp = "/tmp/deface"
    if not os.path.exists(temp): os.mkdir(temp)
    fname_local=os.path.basename(button_mri)
    # establish path to defaced mri files
    defaced_mri = f"{temp}/defaced_{fname_local}"
    # check if they already exist, delete them if they do
    if os.path.exists(defaced_mri):
        os.remove(defaced_mri)
    cmd = f"mri_deface {button_mri} {talairach} {face} {temp}/defaced_{fname_local}"
    subprocess.run(cmd.split(" "))
    # subprocess.run(f"freeview {temp}/defaced_{fname_local}")

    return defaced_mri

def open_window(defaced_mri_path = None):
    # layout = [[sg.Text("Create BIDS", key="new")]]
    layout = [
                [sg.Text(f"Path to defaced MRI:"), sg.InputText(defaced_mri_path), sg.FileBrowse()],
                [sg.Button('View Defaced MRI')],
                [sg.Text('Select the path to MEG .ds folder'), sg.InputText(), sg.FolderBrowse()],
                [sg.Text('Select the path to Transform Matrix'), sg.InputText(), sg.FileBrowse()],
                [sg.Text('Select the path to BIDS output directory'), sg.InputText(), sg.FolderBrowse()],
                [sg.Text('Type run number'), sg.InputText()],
                [sg.Text('Type session number'), sg.InputText()],
                [sg.Text('Type task name'), sg.InputText()],
                [sg.Text('Type bids subject'), sg.InputText()],
                [sg.Button('Ok'), sg.Button('Cancel')]
            ]

    window = sg.Window("Create BIDS", layout, modal=True)
    choice = None
    while True:
        event, values = window.read()
        defaced_mri_path = values[0]

        if event == "Ok":
            window['Ok'].update(disabled=True)
            # defaced_mri_path = values[0]
            meg_ds_path = values[1]
            transform_matrix_path = values[2]
            bids_root_path = values[3]
            run_num = values[4]
            session_num = values[5]
            task_name = values[6]
            bids_subj = values[7]

            wb.write_ctf_bids(
                meg_ds_path,
                run=run_num,
                session=session_num,
                task=task_name,
                bids_subject=bids_subj,
                bids_root=bids_root_path
            )
            
            window['Ok'].update(disabled=False)
            sg.Popup('BIDS Complete!', keep_on_top = True)
            window.close()
            main()
        if event == 'View Defaced MRI':
            subprocess.run(f"freeview {defaced_mri_path}".split(" "))
        if event == "Cancel" or event == sg.WIN_CLOSED:
            break

    window.close()


def main(): # Main Window
    layout = [[sg.Text('Select the path to mri file'), sg.InputText(), sg.FileBrowse()],
            [sg.Button("Deface + Continue", key="open"), sg.Button('Skip'), sg.Button('Cancel')]
            ]
    window = sg.Window("Defacing MRI", layout)
    while True:
        event, values = window.read()

        button_mri = values[0]
        if event == "Cancel" or event == sg.WIN_CLOSED:
            break
        if event == "Skip": 
            mri_path = '' 
            open_window(mri_path)
        if event == "open":
            # deface the mri files
            defaced_mri_path = deface_mri(button_mri)
            # subprocess.run(f"freeview {defaced_mri_path}".split(" "))
            open_window(defaced_mri_path)

    window.close()

def test_deface():
    #  TO DO: MAKE BUTTON_MRI A GLOBAL VARIABLE
    defaced_mri = deface_mri(button_mri)
    assert os.path.exists(defaced_mri)

if __name__ == "__main__":
    main()