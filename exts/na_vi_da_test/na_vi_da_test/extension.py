import omni.ext
import omni.ui as ui
import omni.kit.commands
from pxr import Sdf,Usd
from .img2txt2img import img2txt2img
import numpy as np

TEXTURE_SIZE = 256

OUTPUT_PATH = r"d:\temp\predicted_label_image.png"
MODEL_PATH = r"D:\learn\omni_code\test01\exts\na_vi_da_test\na_vi_da_test\mnist_cnn.pt"

# Functions and vars are available to other extension as usual in python: `example.python_ext.some_public_function(x)`
def draw_circle(image_data, coord_x, coord_y, radius)->np.ndarray:

    TEXTURE_SIZE = image_data.shape[0]

    # Create grids for x and y coordinates
    y, x = np.ogrid[0:TEXTURE_SIZE, 0:TEXTURE_SIZE]

    # Calculate the distance to the center for each point
    distance_to_center = (x - coord_x)**2 + (y - coord_y)**2

    # Identify the points within the circle
    circle_points = distance_to_center <= radius**2

    # Create the circle image with the same initial data as image_data
    circle_image = np.copy(image_data)
    
    # Draw the circle in black (setting it to [0, 0, 0, 255])
    circle_image[circle_points] = [0, 0, 0, 255]

    # Superimpose the circle onto the existing image data
    image_data = np.where(circle_image == [0, 0, 0, 255], circle_image, image_data)
    
    return image_data

# Any class derived from `omni.ext.IExt` in top level module (defined in `python.modules` of `extension.toml`) will be
# instantiated when extension gets enabled and `on_startup(ext_id)` will be called. Later when extension gets disabled
# on_shutdown() is called.
class Na_vi_da_testExtension(omni.ext.IExt):
    
    
    # ext_id is current extension id. It can be used with extension manager to query additional information, like where
    # this extension is located on filesystem.
    
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
        
        self.image_data = draw_circle(self.image_data, x, y, 10)
        
        self.image_data_np = self.image_data.data
        self.provider.set_data_array(self.image_data_np, self.image_data_size)
    
    
    def on_startup(self, ext_id):
        
        self.image_path = ""
        
        self.image_data = np.ones((TEXTURE_SIZE, TEXTURE_SIZE, 4), dtype=np.uint8) * 255
        self.image_data_size = self.image_data.shape[:2]
        self.image_data_np = self.image_data.data
        
        self.provider = ui.ByteImageProvider()
        self.provider.set_data_array(self.image_data_np, self.image_data_size)

        self._window = ui.Window("Textured Cube", width=256, height=720)
        with self._window.frame:
            
            
            with ui.VStack():
                def click_spwan_cube():
                    self.spwan_cube()
                
                def click_load_image():
                    image_path = self.image_path.model.get_value_as_string()
                    
                    print (f"load image: {image_path}")
                    img2txt2img(MODEL_PATH, image_path, OUTPUT_PATH)

                    omni.kit.commands.execute('ChangeProperty',
                    prop_path=Sdf.Path('/World/Looks/OmniPBR/Shader.inputs:diffuse_texture'),
                    value=Sdf.AssetPath(OUTPUT_PATH),
                    prev=None)

                def click_reset():
                    self.clear_all()

                with ui.HStack():
                    ui.Button("Spwan Cube", clicked_fn=click_spwan_cube,width=64,height=64)
                    ui.Button("Reset", clicked_fn=click_reset,width=64,height=64)
                
                with ui.CollapsableFrame("By Image Path"):
                    with ui.VStack():
                        ui.Button("Load Image From Path", clicked_fn=click_load_image)
                        ui.Label("Image Path:")
                        self.image_path = ui.StringField()
                with ui.CollapsableFrame("By Drawing"):
                     with ui.VStack():
                        ui.Button("clear",width=32,height=16, clicked_fn=self.clear_image)
                        self._image = ui.ImageWithProvider(
                        self.provider,
                        width=TEXTURE_SIZE,
                        height=TEXTURE_SIZE,
                        fill_policy=ui.IwpFillPolicy.IWP_PRESERVE_ASPECT_FIT)
                        
                        
                self._image.set_mouse_moved_fn(lambda x, y, b, m: self._on_mouse_pressed(x,y,b))
                self._image.set_mouse_pressed_fn(lambda x, y, b, m: self._on_mouse_pressed(x,y,b))
                                   
    def spwan_cube(self):
        omni.kit.commands.execute('cl')
        self.cube = omni.kit.commands.execute('CreateMeshPrimWithDefaultXform',prim_type='Cube')[1]
        print("##########",self.cube)
    
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
