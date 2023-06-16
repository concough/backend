var gulp = require('gulp');
var gutil = require('gulp-util');
var concat = require('gulp-concat');
var compass = require('gulp-compass');
var gulpif = require('gulp-if');
var uglify = require('gulp-uglify');
var minifyHtml = require('gulp-htmlmin');
var imagemin = require("gulp-imagemin");
var pngcrush = require("imagemin-pngcrush");
var uncss = require('gulp-uncss');
var rename = require('gulp-rename');
var rtlcss = require('rtlcss');
var clean = require('gulp-clean');

var js_sources = ['static/development/components/scripts/*.js'];
var sass_sources = ["static/development/components/sass/*.scss"];
var style_sources = ["static/development/components/sass/style.scss"];
var html_sources = ["static/development/html/**/*.html"];
var images_sources = ["static/development/images/**/*.*"];

var devOutputDir = 'static/development/';
var prodOutputDir = 'static/production/concough/';
var htmlOutputDir = 'templates/';
var imagesOutputDir = prodOutputDir + 'images';

var devSassStyle = "expanded";
var prodSassStyle = "compressed";


gulp.task('js', function () {
    gulp.src(js_sources)
        .pipe(concat('general_noauth.js'))
        .on('error', gutil.log)
        .pipe(gulp.dest(devOutputDir + 'js'))
        .pipe(uglify())
        .on('error', gutil.log)
        .pipe(gulp.dest(prodOutputDir + 'js'));
});

gulp.task('clean-images', function () {
  return gulp.src(imagesOutputDir, {read: false})
    .pipe(clean());
});


gulp.task('images', ['clean-images'], function () {
    gulp.src(images_sources)
        .on('error', gutil.log)
        .pipe(gulp.dest(prodOutputDir + 'images'));
});

gulp.task('clean-html', function () {
  return gulp.src(htmlOutputDir, {read: false})
    .pipe(clean());
});

gulp.task('html', ['clean-html'], function () {
   gulp.src(html_sources)
       .pipe(minifyHtml({
           collapseInlineTagWhitespace: true,
           collapseWhitespace: true,
           minifyCSS: true,
           minifyJS: true,
           removeComments: true,
           removeEmptyAttributes: true,
           removeRedundantAttributes: true,
           removeScriptTypeAttributes: true,
           removeStyleLinkTypeAttributes: true,
           useShortDoctype: true,
           processConditionalComments: true

       }))
       .on('error', gutil.log)
       .pipe(gulp.dest(htmlOutputDir));
});

gulp.task('compass', function () {
    gulp.src(style_sources)
        .pipe(compass({
            sass: devOutputDir + 'components/sass',
            images: devOutputDir + 'images',
            style: devSassStyle,
            relative_assets: true,
            line_comments: false

        }))
        .on('error', gutil.log)
        .pipe(gulp.dest(devOutputDir + 'css'));

    gulp.src(style_sources)
        .pipe(compass({
            sass: devOutputDir + 'components/sass',
            images: devOutputDir + 'images',
            style: prodSassStyle,
            relative_assets: true,
            line_comments: false

        }))
        .on('error', gutil.log)
        .pipe(gulp.dest(prodOutputDir + 'css'));

});

gulp.task('watch', function () {
    // gulp.watch(html_sources, ['html']);
    gulp.watch(js_sources, ['js']);
    gulp.watch(sass_sources, ['compass']);
    gulp.watch(images_sources, ['images']);
});

gulp.task('default', ['compass', 'js', "images", "watch"]);

