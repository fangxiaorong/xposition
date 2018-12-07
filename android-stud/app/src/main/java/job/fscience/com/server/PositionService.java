package job.fscience.com.server;

import android.app.Service;
import android.content.Intent;
import android.os.IBinder;
import com.amap.api.location.*;
import job.fscience.com.xposition1.LoginActivity;
import job.fscience.com.xposition1.XApplication;
import okhttp3.Call;
import okhttp3.Callback;
import okhttp3.Response;

import java.io.IOException;
import java.io.InputStreamReader;
import java.io.LineNumberReader;

public class PositionService extends Service implements AMapLocationListener, Callback {
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
//        option.setLocationPurpose(AMapLocationClientOption.AMapLocationPurpose.SignIn);
        option.setNeedAddress(false);
        option.setGpsFirst(true);
//        option.setOnceLocation(true);
//        option.setOnceLocationLatest(true);
        option.setLocationCacheEnable(false);
        option.setInterval(2000);
        locationClient.setLocationOption(option);
    }

    @Override
    public int onStartCommand(Intent intent, int flags, int startId) {
        locationClient.stopLocation();
        locationClient.startLocation();

        System.out.println("onStartCommand xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx");

        return super.onStartCommand(intent, flags, startId);
    }

    @Override
    public void onLocationChanged(AMapLocation aMapLocation) {
        System.out.println("location callback" + aMapLocation);

        Intent intent = new Intent(ACTION_LOCATION);
        if (aMapLocation != null) {
            if (aMapLocation.getErrorCode() == 0 && aMapLocation.getAccuracy() <= 100 && aMapLocation.getLatitude() > 0 && aMapLocation.getLongitude() > 0) {
//                && aMapLocation.getLocationQualityReport().getGPSStatus() == AMapLocationQualityReport.GPS_STATUS_OK) {
                intent.putExtra("latitude", aMapLocation.getLatitude());
                intent.putExtra("longitude", aMapLocation.getLongitude());
                intent.putExtra("speed", aMapLocation.getSpeed());
                intent.putExtra("address", aMapLocation.getAddress());
                intent.putExtra("city", aMapLocation.getCity());
                intent.putExtra("state", aMapLocation.getErrorCode());

                XApplication.getServerInstance().userUploadPosition(
                        LoginActivity.userInfo.getInteger("id"),
                        aMapLocation.getLatitude(),
                        aMapLocation.getLongitude(), 2, this);
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

    @Override
    public void onFailure(Call call, IOException e) {
    }

    @Override
    public void onResponse(Call call, Response response) throws IOException {
    }
}
