"""
静态文本显示功能测试脚本
测试新添加的 SUB_TEXT_STATIC_DISPLAY 事件功能
"""

import logging
import threading
import time


logger = logging.getLogger("OLED测试模块")


class StaticTextTestRig:
    def __init__(self):
        self.event_bus = EventBus()
        self.threads = []

    def add_thread(self, thread: threading.Thread):
        self.threads.append(thread)

    def start_modules(self):
        logger.info("Starting modules for static text test...")
        for thread in self.threads:
            thread.start()

    def stop_modules(self):
        logger.info("Stopping all modules...")
        self.event_bus.publish("EXIT")
        for thread in self.threads:
            thread.join()
        logger.info("All modules have been stopped.")

    def test_basic_static_text(self):
        """测试基础静态文本显示"""
        logger.info("=== 测试基础静态文本显示 ===")

        # 显示一个简单的静态文本
        self.event_bus.publish(
            "SUB_TEXT_STATIC_DISPLAY",
            {
                "text":"Hello World!",
                "font_size":20,
                "layer_id":"hello_world",
                "z_index":10,
                "position":(0, 0),
                "align":"center",
                "valign":"center",
                "duration":3,  # 3秒后自动消失
            }
        )
        logger.info("显示 'Hello World!' 文本，3秒后消失")
        time.sleep(4)

    def test_different_positions(self):
        """测试不同位置的静态文本"""
        logger.info("=== 测试不同位置的静态文本 ===")

        positions = [
            ("左上", (0, 0), "left", "top"),
            ("中上", (0, 0), "center", "top"),
            ("右上", (0, 0), "right", "top"),
            ("左中", (0, 0), "left", "center"),
            ("中心", (0, 0), "center", "center"),
            ("右中", (0, 0), "right", "center"),
            ("左下", (0, 0), "left", "bottom"),
            ("中下", (0, 0), "center", "bottom"),
            ("右下", (0, 0), "right", "bottom"),
        ]

        for i, (name, pos, align, valign) in enumerate(positions):
            logger.info(f"显示 {name} 位置文本")
            self.event_bus.publish(
                "SUB_TEXT_STATIC_DISPLAY",
                {
                    "text":f"{name}位置",
                    "font_size":16,
                    "layer_id":f"pos_test_{i}",
                    "z_index":10,
                    "position":pos,
                    "align":align,
                    "valign":valign,
                    "duration":2,
                }
            )
            time.sleep(2.5)

    def test_different_font_sizes(self):
        """测试不同字体大小"""
        logger.info("=== 测试不同字体大小 ===")

        font_sizes = [10, 14, 18, 22, 26]

        for size in font_sizes:
            logger.info(f"显示字体大小 {size}px")
            self.event_bus.publish(
                "SUB_TEXT_STATIC_DISPLAY",
                {
                    "text":f"字体 {size}px",
                    "font_size":size,
                    "layer_id":f"font_test_{size}",
                    "z_index":10,
                    "position":(0, 0),
                    "align":"center",
                    "valign":"center",
                    "duration":2,
                }
            )
            time.sleep(2.5)

    def test_multiline_text(self):
        """测试多行文本换行"""
        logger.info("=== 测试多行文本换行 ===")

        long_text = "这是一段很长的文本，用来测试自动换行功能。文本应该能够自动换行到多行显示。This is a long text to test automatic line wrapping functionality."

        self.event_bus.publish(
            "SUB_TEXT_STATIC_DISPLAY",
            {
                "text":long_text,
                "font_size":12,
                "layer_id":"multiline_test",
                "z_index":10,
                "position":(0, 0),
                "align":"left",
                "valign":"top",
                "wrap":True,
                "duration":5,
            }
        )
        logger.info("显示多行换行文本，5秒后消失")
        time.sleep(6)

    def test_overlay_with_expression(self):
        """测试与表情叠加显示"""
        logger.info("=== 测试静态文本与表情叠加 ===")

        # 设置背景表情
        logger.info("设置背景表情为 'happy'")
        self.event_bus.publish("SET_EXPRESSION" ,{"expression":"happy"})
        time.sleep(1)

        # 在表情上叠加静态文本
        overlay_texts = [
            ("状态: 正常", (5, 5), 10, "left", "top"),
            ("电量: 85%", (5, 50), 10, "left", "bottom"),
            ("欢迎使用", (0, 25), 16, "center", "center"),
        ]

        for i, (text, pos, size, align, valign) in enumerate(overlay_texts):
            logger.info(f"叠加显示: {text}")
            self.event_bus.publish(
                "SUB_TEXT_STATIC_DISPLAY",
                {
                    "text":text,
                    "font_size":size,
                    "layer_id":f"overlay_{i}",
                    "z_index":15,  # 高于表情层
                    "position":pos,
                    "align":align,
                    "valign":valign,
                    "duration":3,
                }
            )
            time.sleep(1)

        time.sleep(4)  # 等待所有文本消失

    def test_permanent_display(self):
        """测试永久显示文本"""
        logger.info("=== 测试永久显示文本 ===")

        # 显示一个永久文本（没有duration参数）
        self.event_bus.publish(
            "SUB_TEXT_STATIC_DISPLAY",
            {
                "text":"永久显示",
                "font_size":14,
                "layer_id":"permanent_text",
                "z_index":10,
                "position":(0, 0),
                "align":"center",
                "valign":"center",
            }
        )
        logger.info("显示永久文本（需要手动删除）")
        time.sleep(3)

        # 手动删除永久文本
        logger.info("手动删除永久文本")
        self.event_bus.publish("DELETE_LAYER", {"layer_id":"permanent_text"})
        time.sleep(2)

    def test_custom_colors(self):
        """测试自定义颜色（单色OLED）"""
        logger.info("=== 测试自定义颜色 ===")

        # 测试白字黑底（默认）
        self.event_bus.publish(
            "SUB_TEXT_STATIC_DISPLAY",
            {    
                "text":"白字黑底",
                "font_size":16,
                "layer_id":"white_on_black",
                "z_index":10,
                "position":(0, 10),
                "align":"center",
                "valign":"center",
                "text_color":1,  # 白色
                "bg_color":0,  # 黑色
                "duration":2,
            }
        )
        time.sleep(2.5)

        # 测试黑字白底（反色）
        self.event_bus.publish(
            "SUB_TEXT_STATIC_DISPLAY",
            {
                "text":"黑字白底",
                "font_size":16,
                "layer_id":"black_on_white",
                "z_index":10,
                "position":(0, 10),
                "align":"center",
                "valign":"center",
                "text_color":0,  # 黑色
                "bg_color":1,  # 白色
                "duration":2,
            }
        )
        time.sleep(2.5)

    def run_all_tests(self):
        """运行所有测试"""
        logger.info("开始静态文本显示功能完整测试")

        try:
            # 等待模块初始化
            time.sleep(1)

            # 运行各项测试
            self.test_basic_static_text()
            time.sleep(1)

            self.test_different_positions()
            time.sleep(1)

            self.test_different_font_sizes()
            time.sleep(1)

            self.test_multiline_text()
            time.sleep(1)

            self.test_overlay_with_expression()
            time.sleep(1)

            self.test_permanent_display()
            time.sleep(1)

            self.test_custom_colors()

            logger.info("=== 所有静态文本测试完成 ===")

        except Exception as e:
            logger.error(f"测试过程中发生错误: {e}", exc_info=True)


if __name__ == "__main__":

    # 将项目根目录添加到 sys.path，以解决模块导入问题
    import os, sys
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    
    sys.path.insert(0, project_root)  # 添加项目根目录到 sys.path
    from configs.config import config
    from modules.EventBus import EventBus
    from modules.mod_oled_image import OLEDThread
    from modules.mod_oled_roboeyes import RoboeyesThread
    from modules.mod_oled_text import TextDisplayThread
    sys.path.pop(0)                   # 弹出项目根目录 from sys.path

    # 测试任务管理器
    test_rig = StaticTextTestRig()

    # 加载 OLED 模块
    oled_thread = OLEDThread()
    test_rig.add_thread(oled_thread)

    # 加载 Roboeyes 模块（用于叠加测试）
    roboeyes_thread = RoboeyesThread()
    test_rig.add_thread(roboeyes_thread)

    # 加载 Text Display 模块（包含新的静态文本功能）
    text_display_thread = TextDisplayThread(
        font_path = config.get("text_renderer_font_path"),
        oled_width=128,
        oled_height=64,
        oled_fps=30,
    )
    test_rig.add_thread(text_display_thread)

    # 运行测试
    try:
        test_rig.start_modules()
        test_rig.run_all_tests()
    except KeyboardInterrupt:
        logger.info("用户中断测试")
    except Exception as e:
        logger.error(f"测试过程中发生意外错误: {e}", exc_info=True)
    finally:
        test_rig.stop_modules()
        logger.info("静态文本功能测试结束")
