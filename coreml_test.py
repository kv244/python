import coremltools
from PIL import Image, ImageDraw
import cv2
import numpy as np

# uses ideas from https://elder.dev/posts/open-source-virtual-background/ 

class CoreMl(object):
    """This does some basic image processing using PIL (pillow) Image
    and ML using coretools"""

    _MODE_CHAIR: int = 1
    _MODE_PERSON: int = 2
    _img: object
    _img_draw: object

    def __init__(self, test_mode):
        self.test_mode = test_mode
        return

    def _test_image(self, img_name, model_name):
        mdl = coremltools.models.MLModel(model_name)
        # if isinstance(img_name, str):
        img_in = Image.open(img_name)
        # else:
        #    img_in = img_name

        self._img = img_in.resize((513, 513), Image.NEAREST)
        self._img_draw = ImageDraw.Draw(self._img)
        res = mdl.predict({'image': self._img})
        # print(mdl.get_spec())
        return res

    def _test_wrapper(self, dm: object, di: object) -> None:
        res = self._test_image(di, dm)
        r_out = res.get('semanticPredictions')
        xp, yp = 0, 0

        try:
            iter(r_out)
        except Exception:
            print(res)
        else:
            for x in r_out:  # TODO fix below
                xp = 0
                for y in x:
                    xp += 1
                    if y != 0: # != if you want to mask the dominant object
                        self._img_draw.point([(xp, yp)], fill="black")
                yp += 1

            self._img.show()
            del self._img_draw

    def test(self) -> None:
        """Only entry point into the functionality"""

        if self.test_mode == self._MODE_CHAIR:
            dm = "/Users/julianpetrescu/Documents/trainingDataML/JP_TestImageClassifier.mlmodel"
            di = "/Users/julianpetrescu/Documents/trainingDataML/Test/couches/c2.jpg"
        elif self.test_mode == self._MODE_PERSON:
            dm = "/Users/julianpetrescu/Documents/trainingDataML/DeepLabV3Int8LUT.mlmodel"
            di = "/Users/julianpetrescu/Documents/trainingDataML/Test/batam.jpg"
        else:
            raise Exception("Unknown test mode")
            return

        self._test_wrapper(dm, di)

    def shift_img(self, img, dx, dy):
        img = np.roll(img, dy, axis=0)
        img = np.roll(img, dx, axis=1)
        if dy > 0:
            img[:dy, :] = 0
        elif dy < 0:
            img[dy:, :] = 0
        if dx > 0:
            img[:, :dx] = 0
        elif dx < 0:
            img[:, dx:] = 0
        return img

    def cam_test(self, times):
        """Takes a number of snapshots using OpenCV and runs the ML model against them"""

        height, width = 720, 1280
        cap = cv2.VideoCapture(0)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        cap.set(cv2.CAP_PROP_FPS, 60)
        no = 0
        dml = "/Users/julianpetrescu/Documents/trainingDataML/DeepLabV3Int8LUT.mlmodel"

        while no <= times:
            frame: object
            success, frame = cap.read()  # frame is a matrix
            # to remove and use only frame... this processing should be after the green screen only

            holo = cv2.applyColorMap(frame, cv2.COLORMAP_WINTER)
            bandLength, bandGap = 2, 3
            for y in range(holo.shape[0]):
                if y % (bandLength + bandGap) < bandLength:
                    holo[y, :, :] = holo[y, :, :] * np.random.uniform(0.1, 0.3)

            holo2 = cv2.addWeighted(holo, 0.2, self.shift_img(holo.copy(), 5, 5), 0.8, 0)
            holo2 = cv2.addWeighted(holo2, 0.4, self.shift_img(holo.copy(), -5, -5), 0.6, 0)

            fn = "/Users/julianpetrescu/Documents/trainingDataML/Test/cap" + str(no) + ".jpg"
            cv2.imwrite(fn, holo2)
            no += 1
            self._test_wrapper(dml, fn)


# caller
c = CoreMl(2)
# c.test()
c.cam_test(5)
