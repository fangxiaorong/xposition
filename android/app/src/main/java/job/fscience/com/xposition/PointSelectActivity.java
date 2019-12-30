package job.fscience.com.xposition;

import android.os.Bundle;
import android.view.View;
import android.widget.Button;

import com.amap.api.maps.AMap;
import com.amap.api.maps.MapView;
import com.amap.api.maps.model.LatLng;
import com.amap.api.maps.model.Marker;
import com.amap.api.maps.model.MarkerOptions;

import job.fscience.com.lib.BaseActivity;

public class PointSelectActivity extends BaseActivity {
    Button confirmButton;

    AMap mMap;
    Marker marker;
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_point_select);

        confirmButton = (Button) findViewById(R.id.select_btn);
        confirmButton.setVisibility(View.INVISIBLE);
        confirmButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                //
            }
        });

        MapView mapView = (MapView) findViewById(R.id.map);
        mapView.onCreate(savedInstanceState);// 此方法必须重写
        mMap = mapView.getMap();
        mMap.setOnMapLongClickListener(new AMap.OnMapLongClickListener() {
            @Override
            public void onMapLongClick(LatLng latLng) {
                if (marker != null) {
                    marker.setPosition(latLng);
                } else {
                    MarkerOptions markerOption = new MarkerOptions();
                    markerOption.position(latLng);
                    markerOption.setFlat(true);//设置marker平贴地图效果
                    marker = mMap.addMarker(markerOption);
                }
            }
        });
    }

    public String decodePosition(double latitude, double longitude) {
        double ee = Math.sqrt(0.0066943802290);
        double a = 6378137.0;
        double b = Math.sqrt(a * a * (1 - ee * ee));
        double c = a * a / b;
        double epp = Math.sqrt((a * a - b * b) / b / b);
        //求纬度并转为弧度
        double dLatitude = latitude / 180 * PI;
        //求经度并转为弧度
        double dLongitude = longitude / 180 * PI;
        int deglon = (int)(dLongitude * 180 / PI);                            //转化为经度为了求中央经度
        //求中央经度
        int num = (int) (deglon / 6 + 1); //带号
        double midlong = (6 * num - 3) / 180.0 * PI;                    //中央经线（弧度）

        double lp = dLongitude - midlong;
        double N = c / Math.sqrt(1 + epp * epp * Math.cos(dLatitude) * Math.cos(dLatitude));
//        double M = c / Math.pow(1 + epp * epp * Math.cos(dLatitude) * Math.cos(dLatitude), 1.5);
        double ita = epp * Math.cos(dLatitude);
        double t = Math.tan(dLatitude);
        double Nscnb = N * Math.sin(dLatitude) * Math.cos(dLatitude);
        double Ncosb = N * Math.cos(dLatitude);
        double cosb = Math.cos(dLatitude);

        double m0, m2, m4, m6, m8;
        double a0, a2, a4, a6, a8;
        m0 = a * (1 - ee * ee);
        m2 = 3.0 / 2.0 * m0 * ee * ee;
        m4 = 5.0 / 4.0 * ee * ee * m2;
        m6 = 7.0 / 6.0 * ee * ee * m4;
        m8 = 9.0 / 8.0 * ee * ee * m6;

        a0 = m0 + m2 / 2.0 + 3.0 / 8.0 * m4 + 5.0 / 16.0 * m6 + 35.0 / 128.0 * m8;
        a2 = m2 / 2 + m4 / 2 + 15.0 / 32.0 * m6 + 7.0 / 16.0 * m8;
        a4 = m4 / 8.0 + 3.0 / 16.0 * m6 + 7.0 / 32.0 * m8;
        a6 = m6 / 32.0 + m8 / 16.0;
        a8 = m8 / 128.0;

        double B = dLatitude;
        double sb = Math.sin(B);
        double cb = Math.cos(B);
        double s2b = sb * cb * 2;
        double s4b = s2b * (1 - 2 * sb * sb) * 2;
        double s6b = s2b * Math.sqrt(1 - s4b * s4b) + s4b * Math.sqrt(1 - s2b * s2b);

        double X = a0 * B - a2 / 2.0 * s2b + a4 * s4b / 4.0 - a6 / 6.0 * s6b;                 //X为子午线弧长

        double x = Nscnb * lp * lp / 2.0 + Nscnb * cosb * cosb * Math.pow(lp, 4) * (5 - t * t + 9 * ita * ita +
                4 * Math.pow(ita, 4)) / 24.0 + Nscnb * Math.pow(cosb, 4) * Math.pow(lp, 6) * (61 - 58 * t * t +
                Math.pow(t, 4)) / 720.0 + X;

        double y1 = Ncosb * Math.pow(lp, 1) + Ncosb * cosb * cosb * (1 - t * t + ita * ita) / 6.0 * Math.pow(lp, 3) +
                Ncosb * Math.pow(lp, 5) * Math.pow(cosb, 4) * (5 - 18 * t * t + Math.pow(t, 4) + 14 * ita * ita -
                        58 * ita * ita * t * t) / 120.0;
        //位于中央子午线以西的点的Y坐标均为负值。为避免Y坐标出现负值，可将各带的坐标纵轴向西平移500km（半个投影带的最大宽度不超过500km）。此外，由于采用了分带方法，各带的投影完全相同，具有相同坐标值的点在每个投影带中均有一个对应点，为确定该点在地球上的正确位置，还需要在其横坐标之前加上带号，这样的坐标称为通用坐标。
        y1 += 500000; //位置移动量
        return String.format("%f, %f", x, Double.parseDouble(num + "" + y1));
    }


    double PI = 3.14159265358979324;
    public String toWGS(LatLng latLng) {
        double a = 6378245.0;//克拉索夫斯基椭球参数长半轴a
        double ee = 0.00669342162296594323;//克拉索夫斯基椭球参数第一偏心率平方
        double dLat = this.transformLat(latLng.longitude - 105.0, latLng.latitude - 35.0);
        double dLon = this.transformLon(latLng.longitude - 105.0, latLng.latitude - 35.0);
        double radLat = latLng.latitude / 180.0 * this.PI;
        double magic = Math.sin(radLat);
        magic = 1 - ee * magic * magic;
        double sqrtMagic = Math.sqrt(magic);
        dLat = (dLat * 180.0) / ((a * (1 - ee)) / (magic * sqrtMagic) * this.PI);
        dLon = (dLon * 180.0) / (a / sqrtMagic * Math.cos(radLat) * this.PI);

        return decodePosition(dLat, dLon);
    }
    //转换经度
    public double transformLon(double x, double y) {
        double ret = 300.0 + x + 2.0 * y + 0.1 * x * x + 0.1 * x * y + 0.1 * Math.sqrt(Math.abs(x));
        ret += (20.0 * Math.sin(6.0 * x * this.PI) + 20.0 * Math.sin(2.0 * x * this.PI)) * 2.0 / 3.0;
        ret += (20.0 * Math.sin(x * this.PI) + 40.0 * Math.sin(x / 3.0 * this.PI)) * 2.0 / 3.0;
        ret += (150.0 * Math.sin(x / 12.0 * this.PI) + 300.0 * Math.sin(x / 30.0 * this.PI)) * 2.0 / 3.0;
        return ret;
    }
    //转换纬度
    public double transformLat(double x, double y) {
        double ret = -100.0 + 2.0 * x + 3.0 * y + 0.2 * y * y + 0.1 * x * y + 0.2 * Math.sqrt(Math.abs(x));
        ret += (20.0 * Math.sin(6.0 * x * this.PI) + 20.0 * Math.sin(2.0 * x * this.PI)) * 2.0 / 3.0;
        ret += (20.0 * Math.sin(y * this.PI) + 40.0 * Math.sin(y / 3.0 * this.PI)) * 2.0 / 3.0;
        ret += (160.0 * Math.sin(y / 12.0 * this.PI) + 320 * Math.sin(y * this.PI / 30.0)) * 2.0 / 3.0;
        return ret;
    }
}
