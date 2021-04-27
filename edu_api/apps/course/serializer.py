from rest_framework.serializers import ModelSerializer

from course.models import CourseCategory, Course, Teacher


class CourseCategoryModelSerializer(ModelSerializer):
    """课程分类"""
    class Meta:
        model = CourseCategory
        fields = ["id", "name"]


class TeacherModelSerializer(ModelSerializer):
    """讲师序列化其"""
    class Meta:
        model = Teacher
        fields = ["id", "name", "title", "signature", "image", "brief", "role"]


class CourseModelSerializer(ModelSerializer):
    """课程信息"""

    teacher = TeacherModelSerializer()

    class Meta:
        model = Course
        fields = ["id", "name", "course_img", "students", "lessons", "pub_lessons", "price", "teacher", "lesson_list",
                  "discount_name","real_price", "expire_list"]


class CourseDetailsModelSerializer(ModelSerializer):

    teacher = TeacherModelSerializer()

    class Meta:
        model = Course
        fields = ["id", "name", "course_img", "students", "lessons", "pub_lessons", "price", "teacher", "lesson_info",
                  "active_time","discount_name", "real_price", "level1"]
