package job.fscience.com.xposition;

import android.app.Dialog;
import android.content.Context;
import android.os.Bundle;
import android.view.View;
import android.widget.TextView;
import job.fscience.com.lib.CustomDatePicker;
import job.fscience.com.lib.DoubleSlideSeekBar;

import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.Locale;

public class AnimationSettingDialog extends Dialog {
    AnimationSettingClick callback = null;

    TextView startTimeView;
    TextView endTimeView;
    TextView currentTimeView;

    public AnimationSettingDialog(Context context) {
        super(context);
    }

    public AnimationSettingDialog(Context context, int themeResId) {
        super(context, themeResId);
    }

    public AnimationSettingDialog(Context context, boolean cancelable, OnCancelListener cancelListener) {
        super(context, cancelable, cancelListener);
    }

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        setContentView(R.layout.dialog_animation_setting);

        startTimeView = findViewById(R.id.startTime);
        endTimeView = findViewById(R.id.endTime);

        findViewById(R.id.selectStart).setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                currentTimeView = startTimeView;

                customDatePicker.show(startTimeView.getText().toString(), "2010-01-01 00:00", endTimeView.getText().toString());
            }
        });
        findViewById(R.id.selectEnd).setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                currentTimeView = endTimeView;

                customDatePicker.show(endTimeView.getText().toString(), startTimeView.getText().toString(), now);
            }
        });

        findViewById(R.id.confirm_action).setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                if (callback != null) {
                    callback.onConfirmClick();
                }
                AnimationSettingDialog.this.dismiss();
            }
        });

        findViewById(R.id.cancel_action).setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                AnimationSettingDialog.this.dismiss();
            }
        });

        initDatePicker();
    }

    public void setCallback(AnimationSettingClick callback) {
        this.callback = callback;
    }

    public long getMinValue() {
        long time = 0;
        try {
            time = new SimpleDateFormat("yyyy-MM-dd HH:mm", Locale.CHINA).parse(startTimeView.getText().toString()).getTime();
        } catch (Exception e) {}
        return time;
    }

    public long getMaxValue() {
        long time = 0;
        try {
            time = new SimpleDateFormat("yyyy-MM-dd HH:mm", Locale.CHINA).parse(endTimeView.getText().toString()).getTime();
        } catch (Exception e) {}
        return time;
    }

    public interface AnimationSettingClick {
        void onConfirmClick();
    }

    String now = new SimpleDateFormat("yyyy-MM-dd HH:mm", Locale.CHINA).format(new Date());
    private CustomDatePicker customDatePicker;
    private void initDatePicker() {
        startTimeView.setText(now);
        endTimeView.setText(now);

        customDatePicker = new CustomDatePicker(this.getContext(), new CustomDatePicker.ResultHandler() {
            @Override
            public void handle(String time) { // 回调接口，获得选中的时间
                currentTimeView.setText(time);
            }
        }, "2010-01-01 00:00", now); // 初始化日期格式请用：yyyy-MM-dd HH:mm，否则不能正常运行
        customDatePicker.showSpecificTime(true); // 显示时和分
        customDatePicker.setIsLoop(true); // 允许循环滚动
    }
}
