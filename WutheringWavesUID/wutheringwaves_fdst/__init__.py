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
sv_fdst_today = SV("fdst_today")

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


@sv_fdst.on_command(("fdst", "涩图", "st"))
async def send_images(bot: Bot, ev: Event):
    try:
        # 解析图片数量
        text = ev.text.strip()
        if text.isdigit():
            img_num = int(text)
        else:
            img_num = 5
        img_num = min(10, img_num)

        # 获取今天的日期
        today = datetime.datetime.now().strftime("%Y%m%d")

        # 找到最接近今天的文件夹
        closest_folders = find_closest_date_folders(today, img_num)

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
        img_num = min(10, img_num)

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


@sv_fdst_today.on_command(("今日涩图", "今日图图"))
async def send_images_today(bot: Bot, ev: Event):
    try:
        # 解析输入参数
        text = ev.text.strip()
        offset = 1
        num = 5

        if text:
            parts = text.split()
            if len(parts) == 2:
                # 两个整数：offset num
                try:
                    offset = max(1, int(parts[0]))
                    num = min(10, max(1, int(parts[1])))
                except ValueError:
                    logger.warning(f"解析参数失败: {text}")
            elif len(parts) == 1:
                # 一个整数：num
                try:
                    num = min(10, max(1, int(parts[0])))
                except ValueError:
                    logger.warning(f"解析参数失败: {text}")

        # 获取今天的日期
        today = datetime.datetime.now().strftime("%Y%m%d")

        # 找到最接近今天的文件夹
        closest_folders = find_closest_date_folders(today, 1)

        if not closest_folders:
            await bot.send("未找到任何图片文件夹")
            return

        target_folder = closest_folders[0]
        logger.info(f"使用文件夹: {target_folder}")

        # 获取文件夹中的所有图片文件并按时间逆序排列
        folder_path = os.path.join(IMAGES_ROOT, target_folder)
        if not os.path.exists(folder_path):
            await bot.send("目标文件夹不存在")
            return

        image_files = []
        image_extensions = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp"}

        for file in os.listdir(folder_path):
            if Path(file).suffix.lower() in image_extensions:
                image_files.append(file)

        # 按文件名逆序排列（时间逆序）
        image_files.sort(reverse=True)

        if not image_files:
            await bot.send("目标文件夹中没有图片")
            return

        total_images = len(image_files)
        logger.info(f"文件夹中共有 {total_images} 张图片")

        # 计算分页
        start_index = (offset - 1) * num
        end_index = start_index + num

        # 如果offset过大，返回最后一页
        if start_index >= total_images:
            start_index = max(0, total_images - num)
            end_index = total_images
            logger.info(f"offset过大，返回最后一页: {start_index + 1}-{end_index}")

        # 获取当前页的图片
        current_page_files = image_files[start_index:end_index]

        if not current_page_files:
            await bot.send("没有找到符合条件的图片")
            return

        logger.info(
            f"准备发送第 {start_index + 1}-{end_index} 张图片，共 {len(current_page_files)} 张"
        )

        # 读取并发送图片
        for file_name in current_page_files:
            file_path = os.path.join(folder_path, file_name)
            try:
                with open(file_path, "rb") as f:
                    img_data = f.read()
                    await bot.send(img_data)
            except Exception as e:
                logger.error(f"读取图片失败 {file_path}: {e}")
                continue

        # 发送分页信息
        current_page = (start_index // num) + 1
        total_pages = (total_images + num - 1) // num
        await bot.send(f"第 {current_page}/{total_pages} 页，共 {total_images} 张图片")

    except Exception as e:
        logger.error(f"发送今日图片时出错: {str(e)}")
        await bot.send(f"发送图片时出错: {str(e)}")
