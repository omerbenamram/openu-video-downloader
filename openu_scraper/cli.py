from __future__ import unicode_literals, absolute_import


def main():
    pass
    # if args.only_lessons:
    #     lesson_ids = args.only_lessons
    #     department_name = 'Misc lessons'
    # else:
    #     department_name = scraper.get_department_name(args.department)
    #     lessons = scraper.get_all_lesson_ids_for_department(args.department)
    #     lesson_ids = lessons.keys()
    #
    #     # Create nice txt file with lessons info
    #     output_path = Path(args.output_dir).joinpath(args.root_folder).joinpath(department_name)
    #     os.makedirs(str(output_path), exist_ok=True)
    #     f = Path(args.output_dir).joinpath(args.root_folder).joinpath(department_name).joinpath('Lessons.txt').open('w')
    #     f.write('Lessons for {}'.format(department_name))
    #     f.write('\r\n')
    #     for i, lesson in enumerate(lessons):
    #         f.write('{id}. {name}'.format(id=i, name=lessons[lesson]))
    #         f.write('\r\n')
    #     f.close()
    #
    # lessons_db = shelve.open(os.path.join(args.output_dir, department_name + '_lessons.db'))
    # masterclasses_db = shelve.open(os.path.join(args.output_dir, department_name + '_masterclasses.db'))
    #
    # for lesson_id in lesson_ids:
    #     if lesson_id not in lessons_db:
    #         lessons_db[lesson_id] = scraper.get_lesson_by_id(lesson_id)
    #
    #     if args.fetch_masterclasses:
    #         for masterclass_id in lessons_db[lesson_id].masterclass_ids:
    #             if masterclass_id not in masterclasses_db:
    #                 masterclasses_db[masterclass_id] = scraper.get_masterclass_by_id(masterclass_id)
    #
    # # start downlaoding
    #
    # downloader = AsyncDownloader()
    #
    # for lesson in lessons_db.values():
    #     lesson_output_folder_path = Path(args.output_dir).joinpath(args.root_folder).joinpath(department_name).joinpath(
    #         get_valid_filename(lesson.name))
    #
    #     for lesson_link in lesson.links:
    #         downloader.download_link(lesson_link, lesson_output_folder_path)
    #
    #     if args.fetch_masterclasses:
    #         for masterclass_id in lesson.masterclass_ids:
    #             masterclass = masterclasses_db[masterclass_id]
    #             masterclass_output_folder_path = lesson_output_folder_path.joinpath(
    #                 get_valid_filename(masterclass.name))
    #             if masterclass_output_folder_path.exists():
    #                 masterclass_output_folder_path.with_name(
    #                     masterclass_output_folder_path.name + 'masterclass_{}'.format(masterclass_id))
    #             for masterclass_link in masterclass.links:
    #                 downloader.download_link(masterclass_link, masterclass_output_folder_path)
    #
    # downloader.run()
    #
    # unite_ts_videos(os.path.join(args.output_dir, args.root_folder))
    #
    # scraper.exit()
