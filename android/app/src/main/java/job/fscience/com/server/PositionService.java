package job.fscience.com.server;

import android.app.Service;
import android.content.Intent;
import android.os.IBinder;
import com.amap.api.location.AMapLocation;
import com.amap.api.location.AMapLocationClient;
import com.amap.api.location.AMapLocationClientOption;
import com.amap.api.location.AMapLocationListener;

import java.io.IOException;
import java.io.InputStreamReader;
import java.io.LineNumberReader;

public class PositionService extends Service implements AMapLocationListener {
    public static final String ACTION_LOCATION = "com.fscience.xposition.Location";


    AMapLocationClient locationClient = null;

    @Override
    public IBinder onBind(Intent intent) {
        return null;
    }

    @Override
    public void onCreate() {
        super.onCreate();

        locationClient = new AMapLocationClient(getApplicationContext());
        locationClient.setLocationListener(this);

        AMapLocationClientOption option = new AMapLocationClientOption();
        option.setLocationMode(AMapLocationClientOption.AMapLocationMode.Hight_Accuracy);
        option.setOnceLocation(true);
        option.setOnceLocationLatest(true);
        locationClient.setLocationOption(option);
    }

    @Override
    public int onStartCommand(Intent intent, int flags, int startId) {
        locationClient.startLocation();

        System.out.println("onStartCommand xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx");

        return super.onStartCommand(intent, flags, startId);
    }

    @Override
    public void onLocationChanged(AMapLocation aMapLocation) {
        System.out.println("location callback" + aMapLocation);

        Intent intent = new Intent(ACTION_LOCATION);
        if (aMapLocation != null) {
            if (aMapLocation.getErrorCode() == 0) {
                intent.putExtra("latitude", aMapLocation.getLatitude());
                intent.putExtra("longitude", aMapLocation.getLongitude());
                intent.putExtra("address", aMapLocation.getAddress());
                intent.putExtra("city", aMapLocation.getCity());
                intent.putExtra("state", aMapLocation.getErrorCode());

            } else {
                intent.putExtra("state", aMapLocation.getErrorCode());
                intent.putExtra("errinfo", aMapLocation.getErrorInfo());
            }
        } else {
            intent.putExtra("state", -1);
            intent.putExtra("errinfo", "获取不到位置");
        }
        sendBroadcast(intent);
    }


    private String getMac() {
        String macSerial = null;
        String str = "";

        try {
            Process pp = Runtime.getRuntime().exec("cat /sys/class/net/wlan0/address ");
            InputStreamReader ir = new InputStreamReader(pp.getInputStream());
            LineNumberReader input = new LineNumberReader(ir);

            for (; null != str;) {
                str = input.readLine();
                if (str != null) {
                    macSerial = str.trim();// 去空格
                    break;
                }
            }
        } catch (IOException ex) {
            // 赋予默认值
            ex.printStackTrace();
        }
        return macSerial;
    }
}
