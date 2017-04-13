#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
# generated by wxGlade 0.7.1 on Tue Jun 14 21:58:56 2016
#

import wx

# begin wxGlade: dependencies
import gettext
# end wxGlade

# begin wxGlade: extracode
from images import Images
# end wxGlade

from threading import Thread
import subprocess
import os
import wx.html
import sys


class HtmlWindow(wx.html.HtmlWindow):
   def __init__(self, parent, id, size=(600, 400)):
       wx.html.HtmlWindow.__init__(self,parent, id, size=size)
       if 'gtk2' in wx.PlatformInfo:
           self.SetStandardFonts()

   def OnLinkClicked(self, link):
       wx.LaunchDefaultBrowser(link.GetHref())


aboutText = """<p>SJCAM RAW to DNG/TIFF converter %(converter)s. <br/>
Written by Yan Burman<br/>
</p>"""
#See <a href="http://yanburman.github.io/sjcam_raw2dng">sjcam_raw2dng</a><br/>


class AboutBox(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, -1, _("About"),
             style=wx.DEFAULT_DIALOG_STYLE|wx.THICK_FRAME|wx.RESIZE_BORDER|wx.TAB_TRAVERSAL)
        hwin = HtmlWindow(self, -1, size=(400, 200))

        # The following is true only on Windows.
        if hasattr(subprocess, 'STARTUPINFO'):
            # On Windows, subprocess calls will pop up a command window by default
            # when run from Pyinstaller with the ``--noconsole`` option. Avoid this
            # distraction.
            si = subprocess.STARTUPINFO()
            si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            # Windows doesn't search the path by default. Pass it an environment so
            # it will.
            env = os.environ
        else:
            si = None
            env = None

        vers = dict()
        conv_path = os.path.join(os.path.dirname(sys.argv[0]), 'sjcam_raw2dng')
        vers['converter'] = subprocess.check_output([conv_path, '-v'], stdin=subprocess.PIPE, stderr=subprocess.PIPE, startupinfo=si, env=env).strip()
        hwin.SetPage(aboutText % vers)
        btn = hwin.FindWindowById(wx.ID_OK)
        irep = hwin.GetInternalRepresentation()
        hwin.SetSize((irep.GetWidth() + 25, irep.GetHeight() + 10))
        self.SetClientSize(hwin.GetSize())
        self.CentreOnParent(wx.BOTH)
        self.SetFocus()


def subprocess_thread(main, args):
    wx.CallAfter(main.status_text_ctrl.AppendText, _("Starting conversion") + '\n')
    # The following is true only on Windows.
    if hasattr(subprocess, 'STARTUPINFO'):
        # On Windows, subprocess calls will pop up a command window by default
        # when run from Pyinstaller with the ``--noconsole`` option. Avoid this
        # distraction.
        si = subprocess.STARTUPINFO()
        si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        # Windows doesn't search the path by default. Pass it an environment so
        # it will.
        env = os.environ
    else:
        si = None
        env = None

    try:
        main.proc = subprocess.Popen(args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, startupinfo=si, env=env)
        while main.proc.poll() is None:
            line = main.proc.stdout.readline()
            if line != '':
                wx.CallAfter(main.status_text_ctrl.AppendText, line + '\n')
        main.proc.wait()
        main.proc = None
    except BaseException as exc:
        wx.CallAfter(main.status_text_ctrl.AppendText, str(exc))
    finally:
        main.convert_button.Enable()
        main.abort_button.Disable()



class MainFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        # begin wxGlade: MainFrame.__init__
        kwds["style"] = wx.DEFAULT_FRAME_STYLE
        wx.Frame.__init__(self, *args, **kwds)
        
        # Menu Bar
        self.main_frame_menubar = wx.MenuBar()
        self.File = wx.Menu()
        self.Exit = wx.MenuItem(self.File, wx.ID_EXIT, _("E&xit\tCtrl-Q"), _("Exit"), wx.ITEM_NORMAL)
        self.File.AppendItem(self.Exit)
        self.main_frame_menubar.Append(self.File, _("&File"))
        self.Help = wx.Menu()
        self.About = wx.MenuItem(self.Help, wx.ID_ABOUT, _("&About"), _("About"), wx.ITEM_NORMAL)
        self.Help.AppendItem(self.About)
        self.main_frame_menubar.Append(self.Help, _("&Help"))
        self.SetMenuBar(self.main_frame_menubar)
        # Menu Bar end
        self.logo_bitmap = wx.StaticBitmap(self, wx.ID_ANY, wx.NullBitmap)
        self.src_dir_text_ctrl = wx.TextCtrl(self, wx.ID_ANY, "", style=wx.TE_READONLY)
        self.src_dir_button = wx.Button(self, wx.ID_ANY, _("Source folder"))
        self.dest_dir_text_ctrl = wx.TextCtrl(self, wx.ID_ANY, "", style=wx.TE_READONLY)
        self.dst_folder_button = wx.Button(self, wx.ID_ANY, _("Destination folder"))
        self.tiff_checkbox = wx.CheckBox(self, wx.ID_ANY, _("TIFF"))
        self.dng_checkbox = wx.CheckBox(self, wx.ID_ANY, _("DNG"))
        self.thumb_checkbox = wx.CheckBox(self, wx.ID_ANY, _("Thumbnail"))
        self.convert_button = wx.Button(self, wx.ID_ANY, _("Convert"))
        self.status_text_ctrl = wx.TextCtrl(self, wx.ID_ANY, "", style=wx.TE_MULTILINE | wx.TE_READONLY)
        self.abort_button = wx.Button(self, wx.ID_ANY, _("Abort"))

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_MENU, self.OnClose, self.Exit)
        self.Bind(wx.EVT_MENU, self.OnMenuAbout, self.About)
        self.Bind(wx.EVT_BUTTON, self.OnSrcFolder, self.src_dir_button)
        self.Bind(wx.EVT_BUTTON, self.OnDstFolder, self.dst_folder_button)
        self.Bind(wx.EVT_BUTTON, self.OnConvert, self.convert_button)
        self.Bind(wx.EVT_BUTTON, self.OnAbort, self.abort_button)
        # end wxGlade
        self.images = Images()
        self.logo_bitmap.SetBitmap(self.images.bmp_logo)
        self.proc = None
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        self.SetMinSize(self.GetSize())

    def __set_properties(self):
        # begin wxGlade: MainFrame.__set_properties
        self.SetTitle(_("SJCAM RAW Converter"))
        self.SetSize((600, 300))
        self.src_dir_button.SetFocus()
        self.tiff_checkbox.SetToolTip(wx.ToolTip(_("Convert to TIFF")))
        self.dng_checkbox.SetToolTip(wx.ToolTip(_("Convert to DNG")))
        self.dng_checkbox.SetValue(1)
        self.thumb_checkbox.SetToolTip(wx.ToolTip(_("Create thumbnail (needed by some editors e.g. darktable)")))
        self.abort_button.Enable(False)
        # end wxGlade

    def __do_layout(self):
        # begin wxGlade: MainFrame.__do_layout
        grid_sizer_1 = wx.FlexGridSizer(5, 2, 0, 0)
        grid_sizer_2 = wx.GridSizer(1, 3, 0, 0)
        grid_sizer_1.Add((20, 20), 0, 0, 0)
        grid_sizer_1.Add(self.logo_bitmap, 0, wx.ALIGN_CENTER, 0)
        grid_sizer_1.Add(self.src_dir_text_ctrl, 0, wx.EXPAND, 0)
        grid_sizer_1.Add(self.src_dir_button, 0, wx.ALIGN_RIGHT | wx.EXPAND, 0)
        grid_sizer_1.Add(self.dest_dir_text_ctrl, 0, wx.EXPAND, 0)
        grid_sizer_1.Add(self.dst_folder_button, 0, wx.ALIGN_RIGHT | wx.EXPAND, 0)
        grid_sizer_2.Add(self.tiff_checkbox, 0, 0, 0)
        grid_sizer_2.Add(self.dng_checkbox, 0, 0, 0)
        grid_sizer_2.Add(self.thumb_checkbox, 0, 0, 0)
        grid_sizer_1.Add(grid_sizer_2, 1, 0, 0)
        grid_sizer_1.Add(self.convert_button, 0, wx.ALL | wx.EXPAND, 2)
        grid_sizer_1.Add(self.status_text_ctrl, 0, wx.EXPAND, 0)
        grid_sizer_1.Add(self.abort_button, 0, wx.EXPAND, 0)
        self.SetSizer(grid_sizer_1)
        grid_sizer_1.AddGrowableRow(4)
        grid_sizer_1.AddGrowableCol(0)
        self.Layout()
        self.Centre()
        # end wxGlade

    def OnSrcFolder(self, event):  # wxGlade: MainFrame.<event_handler>
        dialog = wx.DirDialog(self, _('Choose source folder'), style=wx.DD_DEFAULT_STYLE | wx.DD_NEW_DIR_BUTTON)
        if dialog.ShowModal() == wx.ID_OK:
            self.src_dir_text_ctrl.SetValue(dialog.GetPath())
        dialog.Destroy()
        event.Skip()

    def OnDstFolder(self, event):  # wxGlade: MainFrame.<event_handler>
        dialog = wx.DirDialog(self, _('Choose destination folder'), style=wx.DD_DEFAULT_STYLE | wx.DD_NEW_DIR_BUTTON)
        if dialog.ShowModal() == wx.ID_OK:
            self.dest_dir_text_ctrl.SetValue(dialog.GetPath())
        dialog.Destroy()
        event.Skip()

    def OnConvert(self, event):  # wxGlade: MainFrame.<event_handler>
        self.status_text_ctrl.Clear()

        if not self.tiff_checkbox.IsChecked() and not self.dng_checkbox.IsChecked():
            dlg = wx.MessageDialog(self, _('Must select at least one output format (DNG/TIFF)'), _('Error!'), wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            event.Skip()
            return

        args = ['./sjcam_raw2dng']

        if self.tiff_checkbox.IsChecked():
            args.append('-t')

        if self.dng_checkbox.IsChecked():
            args.append('-d')

        if self.thumb_checkbox.IsChecked():
            args.append('-m')

        if not self.dest_dir_text_ctrl.IsEmpty():
            args.append('-o')
            args.append(self.dest_dir_text_ctrl.GetValue())

        if self.src_dir_text_ctrl.IsEmpty():
            dlg = wx.MessageDialog(self, _('Must select source folder'), _('Error!'), wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            event.Skip()
            return

        args.append(self.src_dir_text_ctrl.GetValue())

        self.convert_button.Disable()
        self.abort_button.Enable()

        self.thr = Thread(target=subprocess_thread, args=(self, args))
        self.thr.daemon = True
        self.thr.start()

        event.Skip()

    def OnAbort(self, event):  # wxGlade: MainFrame.<event_handler>
        if self.proc:
            self.proc.kill()
        event.Skip()

    def OnMenuAbout(self, event):  # wxGlade: MainFrame.<event_handler>
        dlg = AboutBox(self)
        dlg.ShowModal()
        dlg.Destroy()
        event.Skip()

    def OnClose(self, event):  # wxGlade: MainFrame.<event_handler>
        self.OnAbort(event)
        self.Destroy()

# end of class MainFrame
class MyApp(wx.App):
    def OnInit(self):
        main_frame = MainFrame(None, wx.ID_ANY, "")
        self.SetTopWindow(main_frame)
        main_frame.Show()
        return True

# end of class MyApp

if __name__ == "__main__":
    locale_path = os.path.join(os.path.dirname(sys.argv[0]), 'locale')
    gettext.install("converter", locale_path, True)

    converter = MyApp(0)
    converter.MainLoop()
