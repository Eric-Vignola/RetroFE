import argparse
import errno
import glob
import os
import shutil
import sys

def copytree(src, dst):
    if os.path.isdir(src):
            if not os.path.exists(dst):
                    mkdir_p(dst)
            for name in os.listdir(src):
                    copytree(os.path.join(src, name),
                                        os.path.join(dst, name))
    else:
            print("COPY: " + dst)
            shutil.copyfile(src, dst)

#def copytree(src, dst, only_if_larger=True, debug=False):
    
    ## If we're copying a file
    #if os.path.isfile(src):
        #folder, fname = os.path.split(dst)
        
        ## if dst folder is missing, create it
        #if not os.path.isdir(folder):
            #os.makedirs(folder)
        
        ## if dst file exists, copy only if larger.
        ## this is an ugly hack to fix duplicate dlls.
        #proceed = True
        #if only_if_larger and os.path.isfile(dst):
            #if os.path.getsize(src) < os.path.getsize(dst):
                #proceed = False
                #print('skip %s'%src)
                
        #if proceed:
            #if not debug:
                #shutil.copy2(src, dst)
            #print('copy %s to %s'%(src,dst))
            
            
    ## recurse down the folder
    #else:
        #for root, folders, files in os.walk(src):

            #for f in files+folders:
                #f  = os.path.join(root,f)
                #f_ = f.replace(src, dst)
                #copytree(f, 
                         #f_, 
                         #only_if_larger=only_if_larger, 
                         #debug=debug)
                


def mkdir_p(path):
    print("CREATE: " + path)
    try:
        os.makedirs(path)

    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise
        
        
#todo: this script needs to be broken up into multiple methods 
#      and should be ported to be more like a class

#####################################################################
# Parse arguments
#####################################################################
parser = argparse.ArgumentParser(description='Bundle up some RetroFE common files.')
parser.add_argument('--os', choices=['windows','linux','mac'], required=True, help='Operating System (windows or linux or mac)')
parser.add_argument('--gstreamer_path', help='Path to gstreamer sdk (i.e. D:/gstreamer')
parser.add_argument('--build', default='full', help='Define what contents to package (full, core, engine, layout, none')
parser.add_argument('--clean', action='store_true', help='Clean the output directory')
parser.add_argument('--compiler', help='Compiler to use (vs, mingw, gcc')

args = parser.parse_args()


# windows needs a gstreamer path set
if args.os == 'windows':
    if not hasattr(args, 'gstreamer_path'):
        print('missing argument --gstreamer_path')
        sys.exit(-1)
      
    gstreamer_path = args.gstreamer_path
    if not gstreamer_path:
        print('missing argument --gstreamer_path')
        sys.exit(-1)
        
    if not os.path.exists(gstreamer_path):
        print('could not find gstreamer libraries: ' + gstreamer_path)
        sys.exit(-1)
else:
    gstreamer_path = None


#####################################################################
# Determine base path os to build
#####################################################################
base_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
common_path = os.path.join(base_path, 'Package', 'Environment', 'Common')
os_path = None

if args.os == 'windows':
    os_path = os.path.join(base_path, 'Package', 'Environment', 'Windows')

elif args.os == 'linux':
    os_path = os.path.join(base_path, 'Package', 'Environment', 'Linux')

elif args.os == 'mac':
    os_path = os.path.join(base_path, 'Package', 'Environment', 'MacOS')

#####################################################################
# Copy layers, artwork, config files, etc for the given os
#####################################################################
output_path = os.path.join(base_path, 'Artifacts', args.os, 'RetroFE')

if os.path.exists(output_path) and hasattr(args, 'clean'):
    shutil.rmtree(output_path)


if args.build != 'none' and not os.path.exists(output_path):
    os.makedirs(output_path)

if args.build == 'full':
    collection_path = os.path.join(output_path, 'collections')
    copytree(common_path, output_path)
    copytree(os_path, output_path)

    mkdir_p(os.path.join(output_path, 'meta', 'mamelist'))

    dirs = [d for d in os.listdir(collection_path) if os.path.isdir(os.path.join(collection_path, d))]
    for collection in dirs:
        if not collection.startswith('_'):
            mkdir_p(os.path.join(output_path, 'collections', collection, 'roms'))
            mkdir_p(os.path.join(output_path, 'collections', collection, 'medium_artwork'))
            mkdir_p(os.path.join(output_path, 'collections', collection, 'medium_artwork', 'artwork_front'))
            mkdir_p(os.path.join(output_path, 'collections', collection, 'medium_artwork', 'artwork_back'))
            mkdir_p(os.path.join(output_path, 'collections', collection, 'medium_artwork', 'medium_back'))
            mkdir_p(os.path.join(output_path, 'collections', collection, 'medium_artwork', 'medium_front'))
            mkdir_p(os.path.join(output_path, 'collections', collection, 'medium_artwork', 'bezel'))
            mkdir_p(os.path.join(output_path, 'collections', collection, 'medium_artwork', 'logo'))
            mkdir_p(os.path.join(output_path, 'collections', collection, 'medium_artwork', 'screenshot'))
            mkdir_p(os.path.join(output_path, 'collections', collection, 'medium_artwork', 'screentitle'))
            mkdir_p(os.path.join(output_path, 'collections', collection, 'medium_artwork', 'video'))
            mkdir_p(os.path.join(output_path, 'collections', collection, 'system_artwork'))

elif args.build == 'layout':
    layout_dest_path = os.path.join(output_path, 'layouts')
    layout_common_path = os.path.join(common_path, 'layouts')
    layout_os_path = os.path.join(os_path, 'layouts')

    if not os.path.exists(layout_dest_path):
        os.makedirs(layout_dest_path)

    if os.path.exists(layout_common_path):
        copytree(layout_common_path, layout_dest_path)

    if os.path.exists(layout_os_path):
        copytree(layout_os_path, layout_dest_path)

#####################################################################
# Copy retrofe executable
#####################################################################
if args.os == 'windows':
    if args.build == 'full' or args.build == 'core' or args.build == 'engine':
        # copy retrofe.exe to core folder
        if(hasattr(args, 'compiler') and args.compiler == 'mingw'):
            src_exe = os.path.join(base_path, 'RetroFE', 'Build', 'retrofe.exe')
        else:
            src_exe = os.path.join(base_path, 'RetroFE', 'Build', 'Release', 'retrofe.exe')

        core_path = os.path.join(output_path, 'core')

        # create the core folder
        if not os.path.exists(core_path):
            os.makedirs(core_path)

        # copy retrofe.exe
        shutil.copy(src_exe, core_path)
        
        # the following files need to be copied for gstreamer to work
        sdl_dll = ['SDL2.dll',
                   'SDL2_image.dll',
                   'libjpeg-9.dll',
                   'libwebp-7.dll',
                   'SDL2_mixer.dll',
                   'libmodplug-1.dll',
                   'libopus-0.dll',
                   'libopusfile-0.dll',
                   'SDL2_ttf.dll',
                   'zlib1.dll']

        gstreamer_dll = ['bz2.dll',
                         'ffi-7.dll',
                         'fribidi-0.dll',
                         'gdk_pixbuf-2.0-0.dll',
                         'gio-2.0-0.dll',
                         'glib-2.0-0.dll',
                         'gmodule-2.0-0.dll',
                         'gobject-2.0-0.dll',
                         'graphene-1.0-0.dll',
                         'gstadaptivedemux-1.0-0.dll',
                         'gstallocators-1.0-0.dll',
                         'gstapp-1.0-0.dll',
                         'gstaudio-1.0-0.dll',
                         'gstbadaudio-1.0-0.dll',
                         'gstbase-1.0-0.dll',
                         'gstbasecamerabinsrc-1.0-0.dll',
                         'gstcheck-1.0-0.dll',
                         'gstcodecparsers-1.0-0.dll',
                         'gstcodecs-1.0-0.dll',
                         'gstcontroller-1.0-0.dll',
                         'gstfft-1.0-0.dll',
                         'gstgl-1.0-0.dll',
                         'gstinsertbin-1.0-0.dll',
                         'gstisoff-1.0-0.dll',
                         'gstmpegts-1.0-0.dll',
                         'gstnet-1.0-0.dll',
                         'gstpbutils-1.0-0.dll',
                         'gstphotography-1.0-0.dll',
                         'gstplayer-1.0-0.dll',
                         'gstreamer-1.0-0.dll',
                         'gstriff-1.0-0.dll',
                         'gstrtp-1.0-0.dll',
                         'gstrtsp-1.0-0.dll',
                         'gstrtspserver-1.0-0.dll',
                         'gstsctp-1.0-0.dll',
                         'gstsdp-1.0-0.dll',
                         'gsttag-1.0-0.dll',
                         'gsttranscoder-1.0-0.dll',
                         'gsturidownloader-1.0-0.dll',
                         'gstvideo-1.0-0.dll',
                         'gstwebrtc-1.0-0.dll',
                         'gthread-2.0-0.dll',
                         'harfbuzz.dll',
                         'intl-8.dll',
                         'json-glib-1.0-0.dll',
                         'libFLAC-8.dll',
                         'libcairo-2.dll',
                         'libcairo-gobject-2.dll',
                         'libcairo-script-interpreter-2.dll',
                         'libcharset-1.dll',
                         'libcroco-0.6-3.dll',
                         'libcrypto-1_1.dll',
                         'libdv-4.dll',
                         'libexpat-1.dll',
                         'libfontconfig-1.dll',
                         'libfreetype-6.dll',
                         'libgcc_s_sjlj-1.dll',
                         'libiconv-2.dll',
                         'libjpeg-8.dll',
                         'libkate-1.dll',
                         'libmp3lame-0.dll',
                         'libmpg123-0.dll',
                         'libogg-0.dll',
                         'liboggkate-1.dll',
                         'libopenjp2.dll',
                         'libpng16-16.dll',
                         'librsvg-2-2.dll',
                         'libsbc-1.dll',
                         'libspandsp-2.dll',
                         'libspeex-1.dll',
                         'libsrt.dll',
                         'libssl-1_1.dll',
                         'libstdc++-6.dll',
                         'libtheora-0.dll',
                         'libtheoradec-1.dll',
                         'libtheoraenc-1.dll',
                         'libtiff-5.dll',
                         'libturbojpeg-0.dll',
                         'libvisual-0.4-0.dll',
                         'libvorbis-0.dll',
                         'libvorbisenc-2.dll',
                         'libvorbisfile-3.dll',
                         'libwavpack-1.dll',
                         'libwinpthread-1.dll',
                         'libxml2-2.dll',
                         'libzbar-0.dll',
                         'nice-10.dll',
                         'openh264-6.dll',
                         'opus-0.dll',
                         'orc-0.4-0.dll',
                         'orc-test-0.4-0.dll',
                         'pango-1.0-0.dll',
                         'pangocairo-1.0-0.dll',
                         'pangoft2-1.0-0.dll',
                         'pangowin32-1.0-0.dll',
                         'pixman-1-0.dll',
                         'psl-5.dll',
                         'soup-2.4-1.dll',
                         'sqlite3-0.dll',
                         'srtp2-1.dll',
                         'usrsctp-1.dll',
                         'z-1.dll']
        
        for dll in gstreamer_dll:
            dll = os.path.join(gstreamer_path, 'bin', dll)
            shutil.copy2(dll, core_path)
            print("DLL COPY: " + dll)
            
        for dll in sorted(glob.glob('%s/lib/gstreamer-1.0/*.dll'%gstreamer_path)):
            shutil.copy2(dll, core_path)
            print("DLL COPY: " + dll)            
            
        third_party_path = os.path.join(base_path, 'RetroFE', 'ThirdParty')
        for dll in sorted(glob.glob('%s/SDL*/**/*.dll'%third_party_path, recursive=True)):
            if os.path.split(dll)[-1] in sdl_dll:
                shutil.copy2(dll, core_path)
                print("DLL COPY: " + dll)                
                
                            
        


elif args.os == 'linux':
    if args.build == 'full' or args.build == 'core' or args.build == 'engine':
        src_exe = os.path.join(base_path, 'RetroFE', 'Build', 'retrofe')
        shutil.copy(src_exe, output_path)

elif args.os == 'mac':
    if args.build == 'full' or args.build == 'core' or args.build == 'engine':
        src_exe = os.path.join(base_path, 'RetroFE', 'Build', 'retrofe')
        shutil.copy(src_exe, output_path)
        app_path = os.path.join(output_path, 'RetroFE.app')
        if not os.path.exists(app_path):
            copytree(os_path, output_path)
        shutil.copy(src_exe, output_path + '/RetroFE.app/Contents/MacOS/')



