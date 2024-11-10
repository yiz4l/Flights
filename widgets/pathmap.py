import sys
from PyQt6.QtWidgets import QApplication, QVBoxLayout, QWidget
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import QUrl
import folium
import base64


class MapWidget(QWidget):
    def __init__(self, coordinates, parent=None):
        super().__init__(parent)

        # 设置布局
        layout = QVBoxLayout(self)

        # 创建 QWebEngineView 以显示地图
        self.map_view = QWebEngineView()
        layout.addWidget(self.map_view)

        # 生成地图
        self.generate_map(coordinates)

    def generate_map(self, coordinates):
        # 确保坐标列表不为空
        if not coordinates:
            raise ValueError("坐标列表不能为空")

        # 创建地图，以第一个坐标为中心，并添加基本地图层
        m = folium.Map(location=coordinates[0], zoom_start=10)
        folium.TileLayer('openstreetmap').add_to(m)  # 添加地图图层确保加载正常

        # 添加每个坐标的标记
        for coord in coordinates:
            folium.Marker(location=coord).add_to(m)

        # 绘制路线
        folium.PolyLine(coordinates, color="blue", weight=2.5, opacity=1).add_to(m)

        # 将地图保存到字符串中而不是文件
        html_data = m.get_root().render()

        # 将 HTML 编码为 base64 以适应 data URI
        encoded = base64.b64encode(html_data.encode('utf-8')).decode('utf-8')
        data_uri = f"data:text/html;base64,{encoded}"

        # 在 QWebEngineView 中加载 HTML 内容
        self.map_view.setUrl(QUrl(data_uri))


# 示例用法
if __name__ == "__main__":
    app = QApplication(sys.argv)

    # 示例坐标列表
    coordinates = [(39.9042, 116.4074), (34.0522, -118.2437), (51.5074, -0.1278)]

    # 创建 MapWidget 并传入坐标列表
    map_widget = MapWidget(coordinates)
    map_widget.resize(800, 600)
    map_widget.setWindowTitle("地图路线显示")
    map_widget.show()

    sys.exit(app.exec())