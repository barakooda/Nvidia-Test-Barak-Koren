import time
import omni.ext
import omni.ui as ui
import omni.kit.commands
from pxr import Sdf,Usd,UsdUtils
from .img2txt2img import img2txt2img
from .circle import draw_circle
from PIL import Image
import numpy as np
from .bug_fixes import fix_cube_uv
TEXTURE_SIZE = 224

OUTPUT_PATH = r"d:\temp\predicted_label_image.png"
MODEL_PATH = r"D:\learn\omni_code\test01\exts\na_vi_da_test\na_vi_da_test\mnist_cnn.pt"

# Functions and vars are available to other extension as usual in python: `example.python_ext.some_public_function(x)`
def wait_for_stage(timeout=10):
    end_time = time.time() + timeout
    while time.time() < end_time:
        stages = UsdUtils.StageCache.Get().GetAllStages()
        if stages:
            return stages[0]
        time.sleep(0.1)  # Sleep for 100 milliseconds before checking again
    return None

# Any class derived from `omni.ext.IExt` in top level module (defined in `python.modules` of `extension.toml`) will be
# instantiated when extension gets enabled and `on_startup(ext_id)` will be called. Later when extension gets disabled
# on_shutdown() is called.
class Na_vi_da_testExtension(omni.ext.IExt):
    
    
    # ext_id is current extension id. It can be used with extension manager to query additional information, like where
    # this extension is located on filesystem.
    def click_spwan_cube(self):
        self.spwan_cube()
                
    def click_load_image(self):
        image_path = self.image_path.model.get_value_as_string()
        
        print (f"load image: {image_path}")
        img2txt2img(MODEL_PATH, image_path, OUTPUT_PATH)

        omni.kit.commands.execute('ChangeProperty',
        prop_path=Sdf.Path('/World/Looks/OmniPBR/Shader.inputs:diffuse_texture'),
        value=Sdf.AssetPath(OUTPUT_PATH),
        prev=None)

    def click_reset(self):
        self.clear_all()
    
    
    def clear_image(self):
        self.image_data.fill(255)
        self.image_data_size = self.image_data.shape[:2]
        self.image_data_np = self.image_data.data
        self.provider.set_data_array(self.image_data_np, self.image_data_size)
        
        print("clear")
    
    def _on_mouse_pressed(self, x, y, key):
        image_pos_x=self._image.screen_position_x
        image_pos_y=self._image.screen_position_y
        x= x - image_pos_x
        y= y - image_pos_y
        
        self.image_data = draw_circle(self.image_data, x, y, 5)
        
        self.image_data_np = self.image_data.data
        self.provider.set_data_array(self.image_data_np, self.image_data_size)
    
    
    def on_startup(self, ext_id):
        
        self.image_path = ""
        
        self.image_data = np.ones((TEXTURE_SIZE, TEXTURE_SIZE, 4), dtype=np.uint8) * 255
        self.image_data_size = self.image_data.shape[:2]
        self.image_data_np = self.image_data.data
        
        self.provider = ui.ByteImageProvider()
        self.provider.set_data_array(self.image_data_np, self.image_data_size)

        self._window = ui.Window("Textured Cube", width=512, height=512)
        
        self.build_window()
                                   
    def spwan_cube(self):
        omni.kit.commands.execute('cl')
        self.cube_path = omni.kit.commands.execute('CreateMeshPrimWithDefaultXform',prim_type='Cube')[1]
        print("##########",self.cube_path)
        stage = wait_for_stage()
        cube = stage.GetPrimAtPath(self.cube_path)
        fix_cube_uv(cube)
    
        self.mat = omni.kit.commands.execute('CreateAndBindMdlMaterialFromLibrary',
            mdl_name='OmniPBR.mdl',
            mtl_name='OmniPBR',
            mtl_created_list=['/World/Looks/OmniPBR'],
            bind_selected_prims=[])
        
        print("##########",self.mat)

        omni.kit.commands.execute('BindMaterial',
            material_path='/World/Looks/OmniPBR',
            prim_path=['/World/Cube'],
            strength=['weakerThanDescendants'])
        
        print("Cube Spwaned")
        
    def clear_all(self)->None:

        omni.kit.commands.execute('DeletePrims',
            paths=[Sdf.Path('/World/Cube')],
            destructive=False)

        omni.kit.commands.execute('DeletePrims',
            paths=[Sdf.Path('/World/Looks')],
            destructive=False)
    
    def on_shutdown(self):
        print("[na_vi_da_test] na_vi_da_test shutdown")
    
    def submit_drwaing(self):        
        image_path = OUTPUT_PATH
        img = Image.fromarray(self.image_data,mode="RGBA")
        img.save(image_path, "PNG")
        img2txt2img(MODEL_PATH, image_path, OUTPUT_PATH)

        omni.kit.commands.execute('ChangeProperty',
        prop_path=Sdf.Path('/World/Looks/OmniPBR/Shader.inputs:diffuse_texture'),
        value=Sdf.AssetPath(OUTPUT_PATH),
        prev=None)
        omni.kit.commands.execute('Group')
        
        
    def build_window(self):
         with self._window.frame:
            with ui.VStack():

                with ui.HStack(height=ui.Percent(5)):
                    ui.Button("Spwan Cube", clicked_fn=self.click_spwan_cube,width=64,height=64)
                    ui.Button("Reset", clicked_fn=self.click_reset,width=64,height=64)
                
                with ui.VStack(height=ui.Percent(20)):
                    with ui.CollapsableFrame("By Image Path"):
                        with ui.VStack():
                            ui.Button("Load Image From Path", clicked_fn=self.click_load_image)
                            ui.Label("Image Path:")
                            self.image_path = ui.StringField()
                with ui.VStack(height=ui.Percent(75)):
                    with ui.CollapsableFrame("By Drawing"):
                        with ui.VStack():
                            with ui.HStack(height=ui.Percent(5)):
                                ui.Button("Submit",width=32,height=16, clicked_fn=self.submit_drwaing)
                                ui.Button("Clear",width=32,height=16, clicked_fn=self.clear_image)
                            self._image = ui.ImageWithProvider(
                            self.provider,
                            width=TEXTURE_SIZE,
                            height=TEXTURE_SIZE,
                            fill_policy=ui.IwpFillPolicy.IWP_PRESERVE_ASPECT_FIT)
                            
                             
                self._image.set_mouse_moved_fn(lambda x, y, b, m: self._on_mouse_pressed(x,y,b))
                self._image.set_mouse_pressed_fn(lambda x, y, b, m: self._on_mouse_pressed(x,y,b))