import os
import random
import datetime
from pathlib import Path
from typing import List, Tuple

from gsuid_core.sv import SV
from gsuid_core.bot import Bot
from gsuid_core.gss import gss
from gsuid_core.models import Event
from gsuid_core.aps import scheduler
from gsuid_core.logger import logger

sv_fdst = SV("fdst")
sv_fdst_roll = SV("fdst_roll")

# 图片根目录
IMAGES_ROOT = "/root/images"


def get_date_folders() -> List[str]:
    """获取所有日期文件夹，按日期排序"""
    if not os.path.exists(IMAGES_ROOT):
        return []

    folders = []
    for item in os.listdir(IMAGES_ROOT):
        item_path = os.path.join(IMAGES_ROOT, item)
        if os.path.isdir(item_path) and item.isdigit() and len(item) == 8:
            folders.append(item)

    return sorted(folders)


def get_images_in_folder(folder_name: str) -> List[bytes]:
    """获取指定文件夹中的所有图片文件的二进制数据"""
    folder_path = os.path.join(IMAGES_ROOT, folder_name)
    if not os.path.exists(folder_path):
        return []

    image_extensions = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp"}
    images = []

    for file in os.listdir(folder_path):
        if Path(file).suffix.lower() in image_extensions:
            file_path = os.path.join(folder_path, file)
            try:
                with open(file_path, "rb") as f:
                    images.append(f.read())
            except Exception as e:
                logger.warning(f"读取图片文件失败 {file_path}: {e}")

    return images


def find_closest_date_folders(target_date: str, num_folders: int) -> List[str]:
    """找到最接近目标日期的指定数量的文件夹"""
    all_folders = get_date_folders()
    if not all_folders:
        return []

    # 计算每个文件夹与目标日期的距离
    folder_distances = []
    for folder in all_folders:
        try:
            folder_date = datetime.datetime.strptime(folder, "%Y%m%d")
            target_datetime = datetime.datetime.strptime(target_date, "%Y%m%d")
            distance = abs((folder_date - target_datetime).days)
            folder_distances.append((folder, distance))
        except ValueError:
            continue

    # 按距离排序
    folder_distances.sort(key=lambda x: x[1])

    # 返回最近的num_folders个文件夹
    return [folder for folder, _ in folder_distances[:num_folders]]


def select_random_images_from_folders(
    folders: List[str], num_images: int
) -> List[bytes]:
    """从指定文件夹中随机选择指定数量的图片二进制数据"""
    all_images = []

    # 收集所有文件夹中的图片
    for folder in folders:
        images = get_images_in_folder(folder)
        all_images.extend(images)

    if not all_images:
        return []

    # 随机选择指定数量的图片
    if len(all_images) <= num_images:
        return all_images
    else:
        return random.sample(all_images, num_images)


def select_random_folders(num_folders: int) -> List[str]:
    """随机选择指定数量的文件夹"""
    all_folders = get_date_folders()
    if not all_folders:
        return []

    if len(all_folders) <= num_folders:
        return all_folders
    else:
        return random.sample(all_folders, num_folders)


@sv_fdst.on_command(("fdst", "今日涩图", "涩图", "st"))
async def send_images(bot: Bot, ev: Event):
    try:
        # 解析图片数量
        text = ev.text.strip()
        if text.isdigit():
            img_num = int(text)
        else:
            img_num = 5

        # 获取今天的日期
        today = datetime.datetime.now().strftime("%Y%m%d")

        # 找到最接近今天的文件夹（最多5个文件夹）
        closest_folders = find_closest_date_folders(today, 5)

        if not closest_folders:
            await bot.send("未找到任何图片文件夹")
            return

        # 从这些文件夹中随机选择图片
        img_list = select_random_images_from_folders(closest_folders, img_num)

        if not img_list:
            await bot.send("未找到任何图片")
            return

        logger.info(f"准备发送 {len(img_list)} 张今日相关图片")

        # 发送图片
        for img_data in img_list:
            await bot.send(img_data)

    except Exception as e:
        logger.error(f"发送图片时出错: {str(e)}")
        await bot.send(f"发送图片时出错: {str(e)}")


@sv_fdst_roll.on_command(("随机涩图", "roll涩图"))
async def send_images_roll(bot: Bot, ev: Event):
    try:
        # 解析图片数量
        text = ev.text.strip()
        if text.isdigit():
            img_num = int(text)
        else:
            img_num = 5

        # 随机选择文件夹（最多10个文件夹以提高性能）
        random_folders = select_random_folders(min(10, len(get_date_folders())))

        if not random_folders:
            await bot.send("未找到任何图片文件夹")
            return

        # 从这些文件夹中随机选择图片
        img_list = select_random_images_from_folders(random_folders, img_num)

        if not img_list:
            await bot.send("未找到任何图片")
            return

        logger.info(f"准备发送 {len(img_list)} 张随机图片")

        # 发送图片
        for img_data in img_list:
            await bot.send(img_data)

    except Exception as e:
        logger.error(f"发送图片时出错: {str(e)}")
        await bot.send(f"发送图片时出错: {str(e)}")
