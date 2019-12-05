
import click
import json
from collections import defaultdict
import random
import os
import boto3
import imageio
from PIL import ImageFont, ImageDraw, Image
import cv2
import numpy as np
from retry.api import retry_call


def generate_url(s3, bucket_name, key):
    return s3.generate_presigned_url(
        ClientMethod = 'get_object',
        Params = {'Bucket' : bucket_name, 'Key' : key},
        ExpiresIn = 3600,
        HttpMethod = 'GET')


@click.command()
@click.argument('filename')
@click.argument('output_dir')
@click.option('--bucket', '-b')
@click.option('--font-size', 'size', type=int, default=8)
@click.option('--keyword')
@click.option('--num', type=int, default=-1)
@click.option('--noplot', is_flag=True)
@click.option('--local')
def main(filename, output_dir, bucket, size, keyword, num, noplot, local):
    os.makedirs(output_dir, exist_ok=True)
    fontpath = 'font/ipaexg.ttf'
    font = ImageFont.truetype(fontpath, size)
    s3 = boto3.client('s3')

    j = json.load(open(filename))

    colors = defaultdict(lambda: (random.randint(128, 255),random.randint(128, 255), random.randint(128, 255)))
    if num > 0:
        j = j[:num]
    for task in j:
        result = task['results'][0]
        resource = task['resources'][0]

        if keyword is not None and keyword not in resource['contents']:
            continue
        if local is None:
            img = retry_call(imageio.imread, fargs=(generate_url(s3, bucket, resource['contents']),), tries=3)
        else:
            img = imageio.imread(os.path.join(local, resource['contents']))
        img = img[:, :, :3][:,:,::-1]
        img = np.ascontiguousarray(img, dtype=np.uint8)
        if not noplot:
            img_pil = Image.fromarray(img)
            draw = ImageDraw.Draw(img_pil)
            x, y = (0, 0)
            username = result['worker']
            w, h = font.getsize(username)
            draw.rectangle((x, y, x + w, y + h), fill=colors[username])
            draw.text((x, y), username, font = font , fill = (0, 0, 0) )
            img = np.array(img_pil)

            print(img.shape)

            for info in result['information']:
                classname = ','.join(["{}:{}".format(question['name'], value['name']) for question in info['questions'] for value in question['value']])
                classname = '{} ({})'.format(classname, info['input_text'])
                print(classname)
                xmin, ymin, xmax, ymax = map(int, (info['rectangle']['x1'], info['rectangle']['y1'], info['rectangle']['x2'], info['rectangle']['y2']))
                print(xmin, ymin, xmax, ymax)
                print(img.shape)
                img = cv2.rectangle(img, (xmin, ymin), (xmax, ymax), colors[classname], 2)
                img_pil = Image.fromarray(img)
                draw = ImageDraw.Draw(img_pil)
                x, y = (xmin, ymin + 4)
                w, h = font.getsize(classname)
                draw.rectangle((x, y, x + w, y + h), fill=colors[classname])
                draw.text((x, y), classname, font = font , fill = (0, 0, 0) )
                img = np.array(img_pil)
        os.makedirs(os.path.join(output_dir, result['worker']), exist_ok=True)
        cv2.imwrite(os.path.join(output_dir, result['worker'], os.path.basename(resource['contents'])), img)


if __name__ == '__main__':
    main()
