import xadmin
from course.models import CourseCategory, Course, Teacher, CourseChapter, CourseLesson, CourseDiscountType, \
    CourseDiscount, CoursePriceDiscount, Activity, CourseExpire


class CourseCategoryModelAdmin(object):
    """
    课程分类
    """
    pass


xadmin.site.register(CourseCategory, CourseCategoryModelAdmin)


class CourseModelAdmin(object):
    """
    专题课程
    """
    pass


xadmin.site.register(Course, CourseModelAdmin)


class TeacherModelAdmin(object):
    """讲师、导师表"""
    pass


xadmin.site.register(Teacher, TeacherModelAdmin)


class CourseChapterModelAdmin(object):
    """课程章节"""
    pass


xadmin.site.register(CourseChapter, CourseChapterModelAdmin)


class CourseLessonModelAdmin(object):
    """课程课时"""
    pass


xadmin.site.register(CourseLesson, CourseLessonModelAdmin)







# 以下是优惠活动相关
class PriceDiscountTypeModelAdmin(object):
    """价格优惠类型"""
    pass

xadmin.site.register(CourseDiscountType, PriceDiscountTypeModelAdmin)


class PriceDiscountModelAdmin(object):
    """价格优惠公式"""
    pass

xadmin.site.register(CourseDiscount, PriceDiscountModelAdmin)


class CoursePriceDiscountModelAdmin(object):
    """商品优惠和活动的关系"""
    pass

xadmin.site.register(CoursePriceDiscount, CoursePriceDiscountModelAdmin)


class ActivityModelAdmin(object):
    """商品活动模型"""
    pass

xadmin.site.register(Activity, ActivityModelAdmin)

xadmin.site.register(CourseExpire)
