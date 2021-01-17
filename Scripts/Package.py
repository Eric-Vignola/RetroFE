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
        shutil.copy2(src_exe, core_path)
        
        # the following files need to be copied for gstreamer to work
        third_party_dlls = ['SDL2-2.0.14/lib/x86/SDL2.dll',
                            'SDL2_image-2.0.5/lib/x86/SDL2_image.dll',
                            'SDL2_image-2.0.5/lib/x86/libjpeg-9.dll',
                            'SDL2_image-2.0.5/lib/x86/libwebp-7.dll',
                            'SDL2_mixer-2.0.4/lib/x86/SDL2_mixer.dll',
                            'SDL2_mixer-2.0.4/lib/x86/libmodplug-1.dll',
                            'SDL2_mixer-2.0.4/lib/x86/libopus-0.dll',
                            'SDL2_mixer-2.0.4/lib/x86/libopusfile-0.dll',
                            'SDL2_ttf-2.0.15/lib/x86/SDL2_ttf.dll',
                            'zlib128-dll/zlib1.dll']

        gstreamer_dlls   = ['bin/bz2.dll',
                            'bin/ffi-7.dll',
                            'bin/fribidi-0.dll',
                            'bin/gdk_pixbuf-2.0-0.dll',
                            'bin/gio-2.0-0.dll',
                            'bin/glib-2.0-0.dll',
                            'bin/gmodule-2.0-0.dll',
                            'bin/gobject-2.0-0.dll',
                            'bin/graphene-1.0-0.dll',
                            'bin/gstadaptivedemux-1.0-0.dll',
                            'bin/gstallocators-1.0-0.dll',
                            'bin/gstapp-1.0-0.dll',
                            'bin/gstaudio-1.0-0.dll',
                            'bin/gstbadaudio-1.0-0.dll',
                            'bin/gstbase-1.0-0.dll',
                            'bin/gstbasecamerabinsrc-1.0-0.dll',
                            'bin/gstcheck-1.0-0.dll',
                            'bin/gstcodecparsers-1.0-0.dll',
                            'bin/gstcodecs-1.0-0.dll',
                            'bin/gstcontroller-1.0-0.dll',
                            'bin/gstfft-1.0-0.dll',
                            'bin/gstgl-1.0-0.dll',
                            'bin/gstinsertbin-1.0-0.dll',
                            'bin/gstisoff-1.0-0.dll',
                            'bin/gstmpegts-1.0-0.dll',
                            'bin/gstnet-1.0-0.dll',
                            'bin/gstpbutils-1.0-0.dll',
                            'bin/gstphotography-1.0-0.dll',
                            'bin/gstplayer-1.0-0.dll',
                            'bin/gstreamer-1.0-0.dll',
                            'bin/gstriff-1.0-0.dll',
                            'bin/gstrtp-1.0-0.dll',
                            'bin/gstrtsp-1.0-0.dll',
                            'bin/gstrtspserver-1.0-0.dll',
                            'bin/gstsctp-1.0-0.dll',
                            'bin/gstsdp-1.0-0.dll',
                            'bin/gsttag-1.0-0.dll',
                            'bin/gsttranscoder-1.0-0.dll',
                            'bin/gsturidownloader-1.0-0.dll',
                            'bin/gstvideo-1.0-0.dll',
                            'bin/gstwebrtc-1.0-0.dll',
                            'bin/gthread-2.0-0.dll',
                            'bin/harfbuzz.dll',
                            'bin/intl-8.dll',
                            'bin/json-glib-1.0-0.dll',
                            'bin/libFLAC-8.dll',
                            'bin/libcairo-2.dll',
                            'bin/libcairo-gobject-2.dll',
                            'bin/libcairo-script-interpreter-2.dll',
                            'bin/libcharset-1.dll',
                            'bin/libcroco-0.6-3.dll',
                            'bin/libcrypto-1_1.dll',
                            'bin/libdv-4.dll',
                            'bin/libexpat-1.dll',
                            'bin/libfontconfig-1.dll',
                            'bin/libfreetype-6.dll',
                            'bin/libgcc_s_sjlj-1.dll',
                            'bin/libiconv-2.dll',
                            'bin/libjpeg-8.dll',
                            'bin/libkate-1.dll',
                            'bin/libmp3lame-0.dll',
                            'bin/libmpg123-0.dll',
                            'bin/libogg-0.dll',
                            'bin/liboggkate-1.dll',
                            'bin/libopenjp2.dll',
                            'bin/libpng16-16.dll',
                            'bin/librsvg-2-2.dll',
                            'bin/libsbc-1.dll',
                            'bin/libspandsp-2.dll',
                            'bin/libspeex-1.dll',
                            'bin/libsrt.dll',
                            'bin/libssl-1_1.dll',
                            'bin/libstdc++-6.dll',
                            'bin/libtheora-0.dll',
                            'bin/libtheoradec-1.dll',
                            'bin/libtheoraenc-1.dll',
                            'bin/libtiff-5.dll',
                            'bin/libturbojpeg-0.dll',
                            'bin/libvisual-0.4-0.dll',
                            'bin/libvorbis-0.dll',
                            'bin/libvorbisenc-2.dll',
                            'bin/libvorbisfile-3.dll',
                            'bin/libwavpack-1.dll',
                            'bin/libwinpthread-1.dll',
                            'bin/libxml2-2.dll',
                            'bin/libzbar-0.dll',
                            'bin/nice-10.dll',
                            'bin/openh264-6.dll',
                            'bin/opus-0.dll',
                            'bin/orc-0.4-0.dll',
                            'bin/orc-test-0.4-0.dll',
                            'bin/pango-1.0-0.dll',
                            'bin/pangocairo-1.0-0.dll',
                            'bin/pangoft2-1.0-0.dll',
                            'bin/pangowin32-1.0-0.dll',
                            'bin/pixman-1-0.dll',
                            'bin/psl-5.dll',
                            'bin/soup-2.4-1.dll',
                            'bin/sqlite3-0.dll',
                            'bin/srtp2-1.dll',
                            'bin/usrsctp-1.dll',
                            'bin/z-1.dll',
                            'lib/gstreamer-1.0/gstavi.dll',
                            'lib/gstreamer-1.0/gstcoreelements.dll',
                            'lib/gstreamer-1.0/gstd3d11.dll',
                            'lib/gstreamer-1.0/gstisomp4.dll',
                            'lib/gstreamer-1.0/gstplayback.dll',
                            'lib/gstreamer-1.0/gsttypefindfunctions.dll',
                            'lib/gstreamer-1.0/gstvideoconvert.dll',
                            'lib/gstreamer-1.0/gstvideoparsersbad.dll']


        for dll in glob.glob('%s/*.dll'%core_path):
            os.remove(dll)
            
        third_party_path = os.path.join(base_path, 'RetroFE', 'ThirdParty')
        for dll in third_party_dlls:
            dll = os.path.join(third_party_path,dll)
            shutil.copy2(dll, core_path)
            print("COPY SDL DLL: " + dll)  
                
        for dll in gstreamer_dlls:
            dll = os.path.join(gstreamer_path, dll)
            shutil.copy2(dll, core_path)
            print("COPY GSTREAMER DLL: " + dll)
            
   
            
              
                
                            
        


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



